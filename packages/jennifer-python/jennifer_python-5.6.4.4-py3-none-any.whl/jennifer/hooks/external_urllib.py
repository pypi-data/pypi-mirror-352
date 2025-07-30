import sys
from jennifer.agent import jennifer_agent
from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'urllib.request'
__minimum_python_version__ = VersionInfo("3.3.0")
_original_urllib_request_urlopen = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    import importlib
    return importlib.import_module(__hooking_module__)


def wrap_urlopen(urlopen):

    def handler(*args, **kwargs):
        o = None
        pi = None

        try:
            from urllib import parse
            from urllib.request import Request

            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                req_obj = args[0]
                if isinstance(req_obj, str):
                    req_obj = Request(req_obj)
                    args = (req_obj,)

                url = req_obj.full_url

                if o is not None:
                    url_info = parse.urlparse(url)
                    pi = o.profiler.start_external_call(
                        call_type=url_info.scheme,
                        url=url,
                        host=url_info.hostname,
                        port=url_info.port or 80,
                        caller='urllib.request.urlopen')

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


def unhook(urllib_module):
    global _original_urllib_request_urlopen

    if _original_urllib_request_urlopen is not None:
        urllib_module.urlopen = _original_urllib_request_urlopen


def hook(urllib_module):
    global __target_version
    __target_version = urllib_module.__version__

    global _original_urllib_request_urlopen
    if 'wrap_urlopen.' in str(urllib_module.urlopen):
        return False

    _original_urllib_request_urlopen = urllib_module.urlopen
    urllib_module.urlopen = wrap_urlopen(urllib_module.urlopen)
    return True
