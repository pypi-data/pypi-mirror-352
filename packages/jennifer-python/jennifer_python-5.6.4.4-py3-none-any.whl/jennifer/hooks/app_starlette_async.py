from .util import _log, VersionInfo
from jennifer.wrap.asgi import wrap_asgi_handler

__hooking_module__ = 'starlette.applications'
__minimum_python_version__ = VersionInfo("3.6.0")
_original_starlette_middleware_module_starlette_call = None
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


def unhook(starlette_middleware_module):
    global _original_starlette_middleware_module_starlette_call

    if _original_starlette_middleware_module_starlette_call is not None:
        from starlette.applications import Starlette
        Starlette.__call__ = _original_starlette_middleware_module_starlette_call


def hook(starlette_middleware_module):
    from starlette.applications import Starlette
    global _original_starlette_middleware_module_starlette_call

    global __target_version
    __target_version = starlette_middleware_module.__version__

    try:
        if 'wrap_asgi_handler.' in str(Starlette.__call__):
            return False

        _original_starlette_middleware_module_starlette_call = Starlette.__call__
        Starlette.__call__ = wrap_asgi_handler(Starlette.__call__)

    except Exception as e:
        _log('ERROR', __hooking_module__, 'hook', e)

    return True
