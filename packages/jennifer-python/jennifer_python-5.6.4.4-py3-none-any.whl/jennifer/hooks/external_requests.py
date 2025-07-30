import sys
from jennifer.agent import jennifer_agent
from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'requests'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_requests_send = None
__target_version = None


global parse_url_func


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


def wrap_send(origin):
    global parse_url_func

    if sys.version_info.major == 3:
        parse_url_func = parse_url3
    else:
        parse_url_func = parse_url2

    def handler(self, request, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()
            if agent is not None:
                o = agent.current_active_object()
                url = request.url

                if o is not None:
                    url_info = parse_url_func(url)
                    pi = o.profiler.start_external_call(
                        call_type=url_info.scheme,
                        host=url_info.hostname,
                        port=url_info.port or 80,
                        url=url,
                        caller='requests.Session.send')

                    if agent.app_config.topology_mode is True:
                        request.headers[agent.app_config.guid_http_header_key] = o.guid

                        request.headers[agent.app_config.topology_http_header_key] = o.outgoing_key
                        request.headers[X_DOMAIN_ID] = o.outgoing_sid
                        request.headers[X_AGENT_ID] = o.outgoing_agent_id
        except Exception as e:
            pass

        err = None
        resp = None

        try:
            resp = origin(self, request, **kwargs)
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

        if err is not None:
            raise err

        return resp
    return handler


def unhook(requests_module):
    global _original_requests_send
    if _original_requests_send is not None:
        requests_module.Session.send = _original_requests_send


def hook(requests_module):
    global _original_requests_send

    global __target_version
    if 'wrap_send.' in str(requests_module.Session.send):
        return False

    __target_version = requests_module.__version__

    _original_requests_send = requests_module.Session.send
    requests_module.Session.send = wrap_send(requests_module.Session.send)
    return True
