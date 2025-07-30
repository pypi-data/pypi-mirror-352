import sys

from jennifer.agent import jennifer_agent
from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'urllib2'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_urllib2_urlopen = None
__target_version = None

global parse_url_func2


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    return __import__(__hooking_module__)


def parse_url2(url):
    from urlparse import urlparse
    return urlparse(url)


def parse_url3(url):
    from urllib import parse
    return parse.urlparse(url)


def wrap_urlopen(urlopen):
    global parse_url_func2

    if sys.version_info.major == 3:
        parse_url_func2 = parse_url3
    else:
        parse_url_func2 = parse_url2

    def handler(*args, **kwargs):
        o = None
        pi = None

        try:
            from urllib2 import Request

            agent = jennifer_agent()
            if agent is not None:
                o = agent.current_active_object()

                req_obj = args[0]
                if isinstance(req_obj, str):
                    req_obj = Request(req_obj)
                    args = (req_obj,)

                url = req_obj.get_full_url()

                if o is not None:
                    url_info = parse_url_func2(url)
                    pi = o.profiler.start_external_call(
                        call_type=url_info.scheme,
                        host=url_info.hostname,
                        port=url_info.port or 80,
                        url=url,
                        caller='urllib2.urlopen')

                    if agent.app_config.topology_mode is True:
                        req_obj.add_header(agent.app_config.guid_http_header_key, o.guid)

                        req_obj.add_header(agent.app_config.topology_http_header_key, o.outgoing_key)
                        req_obj.add_header(X_DOMAIN_ID, o.outgoing_sid)
                        req_obj.add_header(X_AGENT_ID, o.outgoing_agent_id)
        except Exception as e:
            pass

        err = None
        resp = None

        try:
            resp = urlopen(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                key = resp.headers.get(agent.app_config.topology_http_header_key, 0)
                sid = resp.headers.get(X_DOMAIN_ID, 0)
                agent_id = resp.headers.get(X_AGENT_ID, 0)

                o.profiler.end_external_call(pi, err, request_key=key, domain_id=sid, agent_id=agent_id)
        except:
            pass

        return resp
    return handler


def unhook(urllib2_module):
    global _original_urllib2_urlopen
    if _original_urllib2_urlopen is not None:
        urllib2_module.urlopen = _original_urllib2_urlopen


def hook(urllib2_module):
    global __target_version
    __target_version = urllib2_module.__version__

    if not sys.version_info.major == 2:
        return False

    global _original_urllib2_urlopen
    if 'wrap_urlopen.' in str(urllib2_module.urlopen):
        return False

    urllib2_module.urlopen = wrap_urlopen(urllib2_module.urlopen)
    return True
