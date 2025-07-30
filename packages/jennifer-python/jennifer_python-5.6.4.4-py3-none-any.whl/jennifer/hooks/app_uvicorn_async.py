from .util import _log, VersionInfo
from jennifer.wrap.asgi import wrap_asgi_handler

__hooking_module__ = 'uvicorn.middleware.asgi2'
__minimum_python_version__ = VersionInfo("3.6.0")
_original_uvicorn_middleware_module_call = None
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


def unhook(uvicorn_middleware_module):
    global _original_uvicorn_middleware_module_call

    if _original_uvicorn_middleware_module_call is not None:
        from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
        ProxyHeadersMiddleware.__call__ = _original_uvicorn_middleware_module_call


def hook(uvicorn_middleware_module):
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    global _original_uvicorn_middleware_module_call

    global __target_version
    __target_version = uvicorn_middleware_module.__version__

    try:
        if 'wrap_asgi_handler.' in str(ProxyHeadersMiddleware.__call__):
            return False

        _original_uvicorn_middleware_module_call = ProxyHeadersMiddleware.__call__
        ProxyHeadersMiddleware.__call__ = wrap_asgi_handler(ProxyHeadersMiddleware.__call__)

    except Exception as e:
        _log('ERROR', __hooking_module__, 'hook', e)

    return True
