import sys
from jennifer.agent import jennifer_agent
from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'celery'
__minimum_python_version__ = VersionInfo("3.8.0")
_original_celery_async_result_get = None
_original_celery_send_task = None
_original_celery_group_result_get = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    return __import__(__hooking_module__)


def wrap_async_result_get(origin_func):

    def handler(self, *args, **kwargs):
        o = None
        pi = None
        func_name = None

        try:
            func_name = self.call_func_name
        except:
            pass

        try:
            agent = jennifer_agent()
            o = agent.current_active_object()

            if o is not None:
                pi = o.profiler.start_method('celery.result AsyncResult.' + func_name + '.get')
        except:
            pass

        return_value = None
        err = None

        try:
            return_value = origin_func(self, *args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_method(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return return_value
    return handler


def parse_url3(url):
    from urllib import parse
    return parse.urlparse(url)


def get_broker_default_port(scheme):
    if scheme == 'pyamqp' or scheme == 'amqp':
        return 5672
    elif scheme == 'redis':
        return 6379
    elif scheme == 'sqs':
        return 443
    elif scheme == 'zookeeper':
        return 2181
    return 443


def wrap_celery_group_result_get(origin_func):
    def handler(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()
            o = agent.current_active_object()

            if o is not None:
                pi = o.profiler.start_method('celery.result GroupResult.get')
        except:
            pass

        return_value = None
        err = None

        try:
            return_value = origin_func(self, *args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_method(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return return_value
    return handler


def wrap_celery_send_task(origin_func):
    def handler(self, name, *args, **kwargs):
        o = None
        pi = None
        err = None

        try:
            agent = jennifer_agent()
            if agent is not None:
                o = agent.current_active_object()
                broker_url = self.conf['broker_url']
                broker_url = broker_url.rstrip('/') + '/' + name
                url_info = parse_url3(broker_url)

                default_port = get_broker_default_port(url_info.scheme)
                url_port = url_info.port or default_port
                modified_url = url_info.scheme + '://' + url_info.hostname + ':' + str(url_port) + '/' + name

                pi = o.profiler.start_external_call(
                    call_type=REMOTE_CALL_TYPE_CUSTOM,
                    host=url_info.hostname,
                    port=url_port,
                    url=modified_url,
                    caller='Celery.send_task')
        except:
            pass

        try:
            resp = origin_func(self, name, *args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_external_call(pi, err)

            resp.call_func_name = name
        except:
            pass

        if err is not None:
            raise err

        return resp
    return handler


def unhook(celery_module):
    global _original_celery_send_task
    if _original_celery_send_task is not None:
        celery_module.Celery.send_task = _original_celery_send_task

    global _original_celery_async_result_get
    if _original_celery_async_result_get is not None:
        celery_module.result.AsyncResult.get = _original_celery_async_result_get

    global _original_celery_group_result_get
    if _original_celery_group_result_get is not None:
        celery_module.result.GroupResult.get = _original_celery_group_result_get


def hook(celery_module):
    celery_path = celery_module.__path__
    if type(celery_path) is list:
        if len(celery_path) == 0:
            return False

        celery_path = celery_path[0]

    global __target_version
    global _original_celery_async_result_get
    global _original_celery_send_task
    global _original_celery_group_result_get

    __target_version = celery_module.__version__
    access_check = None

    try:
        access_check = celery_module.result
    except:
        sys.path.append(celery_path)

    try:
        import celery.result

        if 'wrap_async_result_get.' in str(celery_module.result.AsyncResult.get):
            return False

        _original_celery_async_result_get = celery_module.result.AsyncResult.get
        celery_module.result.AsyncResult.get = wrap_async_result_get(celery_module.result.AsyncResult.get)

        _original_celery_group_result_get = celery_module.result.GroupResult.get
        celery_module.result.GroupResult.get = wrap_celery_group_result_get(_original_celery_group_result_get)
    except:
        pass

    if access_check is None:
        sys.path.remove(celery_path)

    try:
        _original_celery_send_task = celery_module.Celery.send_task
        celery_module.Celery.send_task = wrap_celery_send_task(_original_celery_send_task)
    except:
        pass

    return True
