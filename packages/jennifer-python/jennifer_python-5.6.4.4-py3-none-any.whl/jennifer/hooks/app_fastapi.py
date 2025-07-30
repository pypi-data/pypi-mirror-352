from .util import _log, _log_tb, VersionInfo

__hooking_module__ = 'fastapi'
__minimum_python_version__ = VersionInfo("3.6.0")
_original_fastapi_module_concurrency_run_in_threadpool = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    return __import__(__hooking_module__)


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def unhook(fastapi_module):
    global _original_fastapi_module_concurrency_run_in_threadpool

    if _original_fastapi_module_concurrency_run_in_threadpool is not None:
        fastapi_module.concurrency.run_in_threadpool = _original_fastapi_module_concurrency_run_in_threadpool


def hook(fastapi_module):
    global _original_fastapi_module_concurrency_run_in_threadpool

    global __target_version
    __target_version = fastapi_module.__version__

    try:
        if '_wrap_run_in_threadpool.' in str(fastapi_module.concurrency.run_in_threadpool):
            return False

        _original_fastapi_module_concurrency_run_in_threadpool = fastapi_module.concurrency.run_in_threadpool
        fastapi_module.concurrency.run_in_threadpool = \
            _wrap_run_in_threadpool(fastapi_module.concurrency.run_in_threadpool)
    except Exception as e:
        _log('ERROR', __hooking_module__, 'hook', e)

    return True


def _wrap_run_in_threadpool(origin_run_in_threadpool):
    from jennifer.agent import jennifer_agent

    async def _handler(*args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()
            ctx_id = agent.get_ctx_id_func()
            func = _safe_get(args, 0) or kwargs.get('func') or None
            o = agent.current_active_object(ctx_id)

            if o is not None:
                pi = o.profiler.start_method("fastapi.concurrency run_in_threadpool." + func.__name__)
        except:
            _log_tb('run_in_threadpool.pre')

        return_value = None
        err = None

        try:
            return_value = await origin_run_in_threadpool(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_method(pi, err)
        except:
            _log_tb('run_in_threadpool.post')

        if err is not None:
            raise err

        return return_value

    return _handler
