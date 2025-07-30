import contextvars
from concurrent.futures import ThreadPoolExecutor
from .util import VersionInfo

__hooking_module__ = 'asyncio'
__minimum_python_version__ = VersionInfo("3.8.0")
__target_version = __minimum_python_version__
_original_concurrent_futures_tpe_submit = None


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    return __import__(__hooking_module__)


def wrap_concurrent_futures_tpe_submit(tpe_submit):

    def handler(self, fn, /, *args, **kwargs):
        ctx_vars = contextvars.copy_context().items()

        def _run_with_context():
            for var, value in ctx_vars:
                var.set(value)
            return fn(*args, **kwargs)

        return tpe_submit(self, _run_with_context)

    return handler


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def unhook(asyncio_module):
    global _original_concurrent_futures_tpe_submit

    if _original_concurrent_futures_tpe_submit is not None:
        ThreadPoolExecutor.submit = _original_concurrent_futures_tpe_submit


def hook(asyncio_module):
    global _original_concurrent_futures_tpe_submit
    if 'wrap_concurrent_futures_tpe_submit.' in str(ThreadPoolExecutor.submit):
        return False

    _original_concurrent_futures_tpe_submit = ThreadPoolExecutor.submit
    ThreadPoolExecutor.submit = wrap_concurrent_futures_tpe_submit(ThreadPoolExecutor.submit)

    return True
