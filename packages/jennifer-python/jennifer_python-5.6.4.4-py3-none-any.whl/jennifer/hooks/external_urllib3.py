import sys
from jennifer.agent import jennifer_agent
from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'urllib3'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_urllib3_poolmanager_request = None
_original_urllib3_poolmanager_urlopen = None
__target_version = None

global parse_url_func3


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


def wrap_request(urlrequest):
    global parse_url_func3

    if sys.version_info.major == 3:
        parse_url_func3 = parse_url3
    else:
        parse_url_func3 = parse_url2

    def handler(*args, **kwargs):
        o = None
        pi = None

        try:
            from urllib3 import response

            agent = jennifer_agent()
            if agent is not None:
                o = agent.current_active_object()
                url = args[2]

                if o is not None:
                    url_info = parse_url_func3(url)
                    pi = o.profiler.start_external_call(
                        call_type=url_info.scheme,
                        url=url,
                        host=url_info.hostname,
                        port=url_info.port or 80,
                        caller='urllib3.PoolManager')

                    header_obj = kwargs.get('headers')

                    if agent.app_config.topology_mode is True:
                        if header_obj is None:
                            header_obj = {agent.app_config.guid_http_header_key: o.guid,
                                          agent.app_config.topology_http_header_key: o.outgoing_key,
                                          X_DOMAIN_ID: o.outgoing_sid,
                                          X_AGENT_ID: o.outgoing_agent_id}
                            kwargs['headers'] = header_obj
                        else:
                            header_obj[agent.app_config.guid_http_header_key] = o.guid
                            header_obj[agent.app_config.topology_http_header_key] = o.outgoing_key
                            header_obj[X_DOMAIN_ID] = o.outgoing_sid
                            header_obj[X_AGENT_ID] = o.outgoing_agent_id

        except Exception as e:
            pass

        err = None
        resp = None

        try:
            resp = urlrequest(*args, **kwargs)
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


def unhook(urllib3_module):
    global _original_urllib3_poolmanager_request
    global _original_urllib3_poolmanager_urlopen

    if _original_urllib3_poolmanager_request is not None:
        urllib3_module.poolmanager.PoolManager.request = _original_urllib3_poolmanager_request

    if _original_urllib3_poolmanager_urlopen is not None:
        urllib3_module.poolmanager.PoolManager.urlopen = _original_urllib3_poolmanager_urlopen


def hook(urllib3_module):
    global __target_version
    __target_version = urllib3_module.__version__

    if not sys.version_info.major == 3:
        return False

    global _original_urllib3_poolmanager_request
    global _original_urllib3_poolmanager_urlopen

    if 'wrap_request.' in str(urllib3_module.poolmanager.PoolManager.request):
        return False

    _original_urllib3_poolmanager_request = urllib3_module.poolmanager.PoolManager.request
    _original_urllib3_poolmanager_urlopen = urllib3_module.poolmanager.PoolManager.urlopen

    urllib3_module.poolmanager.PoolManager.request = wrap_request(urllib3_module.poolmanager.PoolManager.request)
    urllib3_module.poolmanager.PoolManager.urlopen = wrap_request(urllib3_module.poolmanager.PoolManager.urlopen)

    return True
