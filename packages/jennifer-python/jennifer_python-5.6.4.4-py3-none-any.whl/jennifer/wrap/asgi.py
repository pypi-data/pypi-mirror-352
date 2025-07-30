# -*- coding: utf-8 -*-
"""Wsgi Agent for Jennifer APM
"""
import os
import sys
import base64
import struct
import secrets
import traceback
import jennifer.util as util
import cgi
from contextvars import ContextVar
from datetime import datetime
from jennifer.agent import jennifer_agent
import jennifer.agent.agent
from email.utils import formatdate
import time
from jennifer.pconstants import *
from .util import _log
from http.cookies import SimpleCookie
from urllib import parse


REQUEST_CTX_ID_KEY = "request_ctx_id"

wmonid_pack = struct.Struct('>Q')
_request_ctx_id = ContextVar(REQUEST_CTX_ID_KEY, default=None)


def get_request_ctx_id():
    ctx_value = _request_ctx_id.get()
    return ctx_value


def _wrap_asgi_send(original_app_send, active_object, profiler_obj,
                    set_wmonid, wmonid_cookie_postfix, total_seconds_per_year, new_wmonid=None,
                    topology_header_key=None, response_key=None, response_sid=None, response_agent_id=None):
    async def _handler(*args, **kwargs):
        try:
            response_dict = args[0]
            response_type = response_dict.get('type')

            if response_type == 'http.response.start':
                status_code = response_dict.get('status')
                active_object.http_status_code = status_code
                if status_code == 404:
                    profiler_obj.add_service_error_profile(None)

            set_cookie = None

            if set_wmonid:
                expire = formatdate(
                    timeval=time.time() + total_seconds_per_year,
                    localtime=False,
                    usegmt=True
                )

                if type(new_wmonid) == str:
                    new_wmonid_encoded = new_wmonid
                else:
                    new_wmonid_encoded = util.encode_base64_cookie(new_wmonid)

                set_cookie = 'WMONID=%s; expires=%s; Max-Age=%s; path=/%s' % (
                   new_wmonid_encoded, expire, total_seconds_per_year, wmonid_cookie_postfix)
            else:
                if total_seconds_per_year < 0:
                    set_cookie = 'WMONID=deleted; expires=Thu, 01, Jan 1970 00:00:00 GMT; path=/; Max-Age=-1'

            response_headers = response_dict.get('headers')
            if set_cookie is not None:
                if response_headers is not None:
                    response_headers.append((b'Set-Cookie', set_cookie.encode('utf-8')))

            if response_key is not None and response_sid is not None:
                response_headers.append((topology_header_key.encode('utf-8'), response_key.encode('utf-8')))
                response_headers.append((X_DOMAIN_ID.encode('utf-8'), response_sid.encode('utf-8')))
                response_headers.append((X_AGENT_ID.encode('utf-8'), response_agent_id.encode('utf-8')))
        except Exception as e:
            _log('ERROR', 'wrap_asgi_handler.send.pre', e)
            pass

        try:
            await original_app_send(*args, **kwargs)
        except Exception as e:
            _log('ERROR', 'wrap_asgi_handler.send.post', e)

    return _handler


def wrap_django_asgi_handler(original_app_func):
    callable_func = wrap_asgi_handler(original_app_func)

    async def _handler(this_obj, scope, receive, send):
        await callable_func(this_obj, scope, receive, send)

    return _handler


def wrap_asgi_handler(original_app_func):
    async def _handler(*args, **kwargs):
        modargs = args
        candidate_args = []

        scope = None  # scope: {'type': 'lifespan', 'asgi': {'version': '3.0', 'spec_version': '2.0'}, 'state': {}}
        active_object = None

        wmonid_cookie_expire_sec = 31536000
        wmonid_http_only = ''
        wmonid_http_secure = ''

        agent_proxy = None
        profiler = None
        request_id = None

        req_uri = None
        ignore_wrap = False

        try:
            if len(args) == 4:
                scope = args[1]
                receive = args[2]  # <bound method LifespanOn.receive of <uvicorn.lifespan.on.LifespanOn object>>
                candidate_args = [args[0], scope, receive, ]
                start_send = args[3]  # <bound method LifespanOn.send>
            elif len(args) == 3:
                scope = args[0]
                receive = args[1]  # <bound method LifespanOn.receive of <uvicorn.lifespan.on.LifespanOn object>>
                candidate_args = [scope, receive, ]
                start_send = args[2]  # <bound method LifespanOn.send>
            else:
                ignore_wrap = True

            if ignore_wrap is False:
                ignore_wrap = scope['type'] != 'http'
        except:
            pass

        if ignore_wrap is True:
            await original_app_func(*args, **kwargs)
            return

        try:
            req_headers = list_to_dict(scope.get('headers'))

            wmonid, wmonid_encoded, cookie_exists_wmonid = asgi_get_wmonid(req_headers)
            agent_proxy = jennifer_agent()
            if agent_proxy is not None:

                jennifer.agent.agent.Agent.set_context_id_func(agent_proxy, get_request_ctx_id)
                request_id = _request_ctx_id.set(int.from_bytes(secrets.token_bytes(4), "big"))

                req_uri = scope['path']
                service_naming_http_header_key = agent_proxy.app_config.service_naming_by_http_header
                if service_naming_http_header_key is not None:
                    http_header_uri = req_headers.get(service_naming_http_header_key)
                    if http_header_uri is not None:
                        req_uri = "/" + http_header_uri

                if agent_proxy.app_config.enable_http_only_for_wmonid_cookie:
                    wmonid_http_only = '; HttpOnly'
                if agent_proxy.app_config.enable_secure_for_wmonid_cookie:
                    wmonid_http_secure = '; Secure'
                wmonid_cookie_expire_sec = agent_proxy.app_config.expire_date_for_wmonid_cookie * 24 * 60 * 60

            wmonid_cookie_append = wmonid_http_only + wmonid_http_secure
            if len(wmonid_cookie_append.strip()) == 0:
                wmonid_cookie_append = ';'

            topology_header_key = agent_proxy.app_config.topology_http_header_key
            method_value_length = agent_proxy.app_config.profile_method_return_value_length

            additional_url_keys = agent_proxy.app_config.url_additional_request_keys

            query_params = query_params_to_dict(scope.get('query_string'))
            if additional_url_keys is not None and len(additional_url_keys) > 0:
                req_uri = util.process_url_additional_request_keys(query_params, req_uri,
                                                                   additional_url_keys, method_value_length)

            ignore_req = util.is_ignore_urls(agent_proxy, req_uri)

            response_key = None
            response_sid = None
            response_agent_id = None

            if ignore_req is False:
                active_object = agent_proxy.start_trace(req_headers, wmonid, req_uri)

                if active_object is not None:
                    if agent_proxy.app_config.enable_multi_tier_trace:
                        active_object.guid = req_headers.get(agent_proxy.app_config.guid_http_header_key)
                        if agent_proxy.app_config.topology_mode:
                            incoming_key = req_headers.get(agent_proxy.app_config.topology_http_header_key)
                            response_key = incoming_key
                            incoming_sid = req_headers.get(X_DOMAIN_ID)
                            incoming_agent_id = req_headers.get(X_AGENT_ID)
                            call_type_id = req_headers.get(X_CALLTYPE_ID)
                            response_sid = agent_proxy.domain_id
                            response_agent_id = agent_proxy.agent_id

                            active_object.set_incoming_info(
                                call_type_id, incoming_key, incoming_sid, incoming_agent_id)

                    active_object.initialize("asgi http.handler")
                    profiler = active_object.profiler
                    if agent_proxy.app_config.dump_http_query:
                        profiler.add_message('[%s] %s' % (scope.get('method'), scope.get('path')))

                    header_value_length = agent_proxy.app_config.profile_http_value_length

                    if agent_proxy.app_config.profile_http_header_all:
                        profile_http_all_header(active_object, req_headers, header_value_length)
                    elif agent_proxy.app_config.profile_http_header is not None and\
                            len(agent_proxy.app_config.profile_http_header) != 0:
                        profile_http_partial_header(active_object, req_headers,
                                                    agent_proxy.app_config.profile_http_header,
                                                    header_value_length)

                    param_list = agent_proxy.app_config.profile_http_parameter
                    if param_list is not None and len(param_list) > 0:
                        util.profile_http_parameter_message(active_object, query_params, param_list,
                                                            header_value_length)

                    candidate_args.append(
                        _wrap_asgi_send(start_send,
                                        active_object=active_object,
                                        profiler_obj=profiler,
                                        set_wmonid=(cookie_exists_wmonid is False),
                                        wmonid_cookie_postfix=wmonid_cookie_append,
                                        total_seconds_per_year=wmonid_cookie_expire_sec,
                                        new_wmonid=wmonid_encoded,
                                        topology_header_key=topology_header_key, response_key=response_key,
                                        response_sid=response_sid, response_agent_id=response_agent_id)
                    )

                modargs = candidate_args
        except Exception as e:
            tb = traceback.format_exc()
            _log('ERROR', 'wrap_asgi_handler', e, tb)

        err = None

        try:
            await original_app_func(*modargs, **kwargs)
        except Exception as e:
            err = e

        if profiler is None:
            if request_id is not None:
                _request_ctx_id.reset(request_id)

            if err is not None:
                raise err

            return

        if err is not None:
            if hasattr(err, '__traceback__'):
                ex_result = traceback.format_exception(type(err), err, err.__traceback__)
                ex_result = ''.join(ex_result)
            else:
                ex_result = str(err)
            profiler.add_service_error_profile("Service Error: " + ex_result)

        try:
            if active_object is not None:
                agent_proxy.end_trace(active_object)
                agent_proxy.consume_apc_queue()
        except Exception as e:
            _log('ERROR', 'wrap_asgi_handler.post', e)

        if request_id is not None:
            _request_ctx_id.reset(request_id)

        if err is not None:
            raise err

    return _handler


def query_params_to_dict(query_string):
    if query_string is None:
        return None

    text = query_string.decode('utf-8')
    result = parse.parse_qs(text)

    result = {k: ','.join(v) for k, v in result.items()}
    return result


def list_to_dict(list_value):
    if list_value is None:
        return None

    return {k.decode('utf-8'): v.decode('utf-8') for k, v in list_value}


def asgi_get_wmonid(headers):
    wmon_id_value = None
    wmon_id_encoded = None

    if headers is None:
        return None, None, False

    cookie = headers.get('cookie')
    cookie_wmonid = None

    if cookie is not None:
        cookie = SimpleCookie(cookie)
        cookie_wmonid = cookie.get('WMONID')

    if cookie_wmonid is not None:
        try:
            wmon_id_encoded = cookie_wmonid.value
            wmon_id_value, = wmonid_pack.unpack(util.decode_base64_cookie(wmon_id_encoded))
        except Exception as e:
            _log('ERROR', 'asgi_get_wmonid', cookie_wmonid, e)
            cookie_wmonid = None

    if wmon_id_value is None:
        wmon_id_value = (os.getpid() << 32) + int(time.time())
        wmon_id_encoded = wmonid_pack.pack(wmon_id_value)

    return wmon_id_value, wmon_id_encoded, cookie_wmonid is not None


def profile_http_partial_header(o, environ, header_list, header_max_length):
    text = []

    for header_key in header_list:
        header_value = environ.headers.get(header_key)
        if header_value is not None:
            text.append(header_key + '=' + util.truncate_value(header_value, header_max_length))

    if len(text) != 0:
        o.profiler.add_message('HTTP-HEAD: ' + '; '.join(text))


def profile_http_all_header(o, req_header, header_max_length):
    text = []

    for (key, value) in req_header.items():
        text.append(key + '=' + util.truncate_value(value, header_max_length))

    if len(text) != 0:
        o.profiler.add_message('HTTP-HEAD: ' + '; '.join(text))
