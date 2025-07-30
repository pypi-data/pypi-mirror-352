# -*- coding: utf-8 -*-
"""Wsgi Agent for Jennifer APM
"""
import os
import sys
import base64
import struct
import traceback
import jennifer.util as util
import cgi
from datetime import datetime
from jennifer.agent import jennifer_agent
from email.utils import formatdate
import time
from jennifer.pconstants import *
from .util import _log

try:
    import Cookie as cookies
except ImportError:
    from http import cookies

wmonid_pack = struct.Struct('>Q')


def _wrap_wsgi_start_response(origin, set_wmonid, wmonid_cookie_postfix, total_seconds_per_year, new_wmonid=None,
                              topology_header_key=None, response_key=None,
                              response_sid=None, response_agent_id=None):
    def handler(*args, **kwargs):
        if set_wmonid:
            if len(args) == 2:
                expire = formatdate(
                    timeval=time.time() + total_seconds_per_year,
                    localtime=False,
                    usegmt=True
                )
                set_cookie = 'WMONID=%s; expires=%s; Max-Age=%s; path=/%s' % (
                    util.encode_base64_cookie(new_wmonid), expire, total_seconds_per_year, wmonid_cookie_postfix)
                args[1].append(('Set-Cookie', str(set_cookie)))
        else:
            if total_seconds_per_year < 0 and len(args) == 2:
                set_cookie = 'WMONID=deleted; expires=Thu, 01, Jan 1970 00:00:00 GMT; path=/; Max-Age=-1'
                args[1].append(('Set-Cookie', str(set_cookie)))

        if response_key is not None and response_sid is not None:
            args[1].append((topology_header_key, str(response_key)))
            args[1].append((X_DOMAIN_ID, str(response_sid)))
            args[1].append((X_AGENT_ID, str(response_agent_id)))

        return origin(*args, **kwargs)
    return handler


def _wrap_wsgi_handler(original_app_func):
    def handler(*args, **kwargs):
        environ = {}
        modargs = args
        candidate_args = []
        wmonid = None
        start_response = None
        active_object = None
        ret = None

        incoming_key = None
        incoming_sid = None
        incoming_agent_id = None
        call_type_id = None
        agent = None

        try:
            agent = jennifer_agent()

            new_wmonid_val = (os.getpid() << 32) + int(time.time())
            new_wmonid = wmonid_pack.pack(new_wmonid_val)

            if len(args) == 3:
                environ = args[1]  # self, environ, start_response
                candidate_args = [args[0], args[1], ]
                start_response = args[2]
            elif len(args) == 2:
                environ = args[0]  # environ, start_response
                candidate_args = [args[0], ]
                start_response = args[1]

            url_scheme = environ.get('wsgi.url_scheme')
            http_method = environ.get('REQUEST_METHOD')
            host_host = environ.get('HTTP_HOST')
            req_uri = environ.get('PATH_INFO')
            ignore_req = util.is_ignore_urls(agent, req_uri)

            cookie = cookies.SimpleCookie()
            cookie.load(environ.get('HTTP_COOKIE', ''))
            cookie_wmonid = cookie.get('WMONID')
            if cookie_wmonid is None:
                wmonid = new_wmonid_val
            else:
                try:
                    wmonid, = wmonid_pack.unpack(util.decode_base64_cookie(cookie_wmonid.value))
                except Exception as e:  # incorrect wmonid
                    _log('ERROR', 'get_wmonid', cookie_wmonid, e)
                    cookie_wmonid = None
                    wmonid = new_wmonid_val

            wmonid_http_only = ''
            wmonid_http_secure = ''

            wmonid_cookie_expire_sec = 31536000
            if agent is not None:
                if agent.app_config.enable_http_only_for_wmonid_cookie:
                    wmonid_http_only = '; HttpOnly'
                if agent.app_config.enable_secure_for_wmonid_cookie:
                    wmonid_http_secure = '; Secure'
                wmonid_cookie_expire_sec = agent.app_config.expire_date_for_wmonid_cookie * 24 * 60 * 60

            wmonid_cookie_append = wmonid_http_only + wmonid_http_secure
            if len(wmonid_cookie_append.strip()) == 0:
                wmonid_cookie_append = ';'

            topology_header_key = agent.app_config.topology_http_header_key
            response_key = None
            response_sid = None
            response_agent_id = None

            if agent.app_config.enable_multi_tier_trace and agent.app_config.topology_mode:
                incoming_key = environ.get('HTTP_' +
                                           replace_wsgi_header(agent.app_config.topology_http_header_key))
                incoming_sid = environ.get('HTTP_' + replace_wsgi_header(X_DOMAIN_ID))
                incoming_agent_id = environ.get('HTTP_' + replace_wsgi_header(X_AGENT_ID))
                call_type_id = environ.get('HTTP_' + replace_wsgi_header(X_CALLTYPE_ID))

                response_key = incoming_key
                response_sid = agent.domain_id
                response_agent_id = agent.agent_id

            candidate_args.append(
                _wrap_wsgi_start_response(start_response,
                                          set_wmonid=(cookie_wmonid is None),
                                          wmonid_cookie_postfix=wmonid_cookie_append,
                                          total_seconds_per_year=wmonid_cookie_expire_sec,
                                          new_wmonid=new_wmonid,
                                          topology_header_key=topology_header_key, response_key=response_key,
                                          response_sid=response_sid, response_agent_id=response_agent_id)
            )

            if not ignore_req and agent is not None:
                agent.consume_apc_queue()

                additional_url_keys = agent.app_config.url_additional_request_keys
                method_value_length = agent.app_config.profile_method_return_value_length
                service_naming_http_header_key = agent.app_config.service_naming_by_http_header

                if service_naming_http_header_key is not None:
                    http_header_uri = environ.get('HTTP_' + service_naming_http_header_key)
                    if http_header_uri is not None:
                        req_uri = "/" + http_header_uri

                if additional_url_keys is not None and len(additional_url_keys) > 0:
                    req_uri = process_url_additional_request_keys(environ, req_uri, additional_url_keys,
                                                                  method_value_length)

                active_object = agent.start_trace(environ, wmonid, req_uri)
                if active_object is not None:
                    if agent.app_config.enable_multi_tier_trace:
                        active_object.guid = environ.get('HTTP_' + agent.app_config.guid_http_header_key)

                    active_object.set_incoming_info(call_type_id, incoming_key, incoming_sid, incoming_agent_id)
                    active_object.initialize("wsgi_handler")
                    if agent.app_config.dump_http_query:
                        req_uri_msg = '[%s] %s://%s%s' % (http_method, url_scheme, host_host, req_uri)
                        active_object.profiler.add_message(req_uri_msg)

                    header_value_length = agent.app_config.profile_http_value_length
                    if agent.app_config.profile_http_header_all:
                        active_object.profiler.add_message("HTTP-HEAD: " +
                                                           get_http_header_from_wsgi(environ, header_value_length))
                    elif agent.app_config.profile_http_header is not None and\
                            len(agent.app_config.profile_http_header) != 0:
                        profile_http_header_message(active_object, environ, agent.app_config.profile_http_header,
                                                    header_value_length)

                    param_list = agent.app_config.profile_http_parameter
                    if param_list is not None and len(param_list) > 0:
                        profile_http_parameter_message(active_object, environ, param_list, header_value_length)

            modargs = candidate_args
        except Exception as e:
            _log('ERROR', 'wsgi_handler', e)

        err = None
        try:
            ret = original_app_func(*modargs, **kwargs)
        except Exception as e:
            err = e  # wsgi 내부에서는 원래 예외가 발생하지 않음!

        if active_object is not None and hasattr(ret, 'status_code'):
            active_object.http_status_code = ret.status_code

            if ret.status_code == 404:
                active_object.profiler.add_service_error_profile(None)
            elif ret.status_code >= 400:
                ex_result = ''
                if hasattr(ret, 'current_exception_info'):
                    cei = ret.current_exception_info
                    if hasattr(cei, '__traceback__'):
                        ex_result = traceback.format_exception(type(cei), cei, cei.__traceback__)
                        ex_result = ''.join(ex_result)
                    else:
                        ex_result = str(cei)
                active_object.profiler.add_service_error_profile("Service Error: " +
                                                                 ret.reason_phrase + " " + ex_result)

        try:
            if active_object is not None:
                agent.end_trace(active_object)
        except Exception as e:
            _log('ERROR', e)

        if err is not None:
            raise err

        return ret
    return handler


def profile_http_header_message(o, environ, header_list, header_value_length):
    text = []

    for header_key in header_list:
        header_value = environ.get('HTTP_' + replace_wsgi_header(header_key))
        if header_value is not None:
            text.append(header_key + '=' + util.truncate_value(header_value, header_value_length))

    if len(text) != 0:
        o.profiler.add_message('HTTP-HEAD: ' + '; '.join(text))


def replace_wsgi_header(header_key):
    return header_key.replace('-', '_').upper()


def process_url_additional_request_keys(environ_dict, req_uri, key_list, method_value_length):
    qs = cgi.parse(environ=environ_dict)
    return util.process_url_additional_request_keys(qs, req_uri, key_list, method_value_length)


def profile_http_parameter_message(o, environ_dict, param_list, header_value_length):
    qs = cgi.parse(environ=environ_dict)
    util.profile_http_parameter_message(o, qs, param_list, header_value_length)


def get_http_header_from_wsgi(environ_dict, header_value_length):
    ret = []
    for k, v in environ_dict.items():
        if k.find('.') != -1:
            continue

        if k.startswith('HTTP_'):
            k = k[5:]

        ret.append(k + '=' + util.truncate_value(v, header_value_length))

    return ';'.join(ret)


def wrap_wsgi_app(original_app_func):
    return _wrap_wsgi_handler(original_app_func)

