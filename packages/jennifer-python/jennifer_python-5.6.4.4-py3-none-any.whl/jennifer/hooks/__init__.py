# -*- coding: utf-8 -*-

import os
import sys
from jennifer.pconstants import *
import platform
from .util import _log, _diag_log, VersionInfo

__current_python_ver__ = VersionInfo(platform.python_version())
__hooked_module__ = {}
python36_version = VersionInfo("3.6.0")

_original_builtins_open = None
_original_builtins_print = None
_original_builtins_socket_connect = None
_original_builtins_socket_connect_ex = None

from jennifer.agent import jennifer_agent

from . import app_flask
from . import db_sqlite3
from . import app_django
from . import db_mysqlclient
from . import db_pymysql
from . import external_requests
from . import external_urllib
from . import external_urllib2
from . import external_urllib3
from . import db_pymongo
from . import db_pymssql
from . import db_redis
from . import db_cx_oracle
from . import db_oracledb
from . import db_psycopg2
from . import db_pyodbc
from . import external_celery
# from . import mod_uvloop

HOOK_SUPPORT_LIST = [
    (app_flask, True),
    (app_django, True),
    (db_mysqlclient, False),
    (db_pymysql, False),
    (db_sqlite3, False),
    (db_pymongo, False),
    (db_pymssql, False),
    (db_psycopg2, False),
    (db_cx_oracle, False),
    (db_oracledb, False),
    (db_redis, False),
    (db_pyodbc, False),
    (external_urllib, False),
    (external_urllib2, False),
    (external_urllib3, False),
    (external_requests, False),
    (external_celery, False),
    # (mod_uvloop, False),
]

if python36_version <= __current_python_ver__:
    try:
        from . import app_fastapi
        HOOK_SUPPORT_LIST.append((app_fastapi, True))
    except:
        pass

    try:
        from . import mod_asyncio
        HOOK_SUPPORT_LIST.append((mod_asyncio, False))
    except:
        pass

    try:
        if os.getenv('starlette_router') == '1':
            from . import app_starlette_async
            HOOK_SUPPORT_LIST.append((app_starlette_async, True))
    except:
        pass

    try:
        from . import app_uvicorn_async
        HOOK_SUPPORT_LIST.append((app_uvicorn_async, True))
    except:
        pass

def _is_module_exist(m):
    module_name = m.__hooking_module__

    try:
        if module_name not in sys.modules:
            _diag_log('INFO', 'loading module:', module_name)
            return m.import_module()

        return sys.modules[module_name]  # RecursionError('maximum recursion depth exceeded')
    except ImportError as e:
        _diag_log('INFO', 'no module:', module_name)
        return False


def unhooking():
    global __hooked_module__

    if len(__hooked_module__) != 0:
        for mod_name in __hooked_module__.keys():
            hook_module = __hooked_module__[mod_name]['hook_module']
            target_module = __hooked_module__[mod_name]['target_module']

            try:
                if hook_module is not None and target_module is not None:
                    hook_module.unhook(target_module)
            except Exception as e:
                _log('ERROR', 'unhooking', e)

    __hooked_module__ = {}
    _unhook_builtins()


def hooking(agent_obj, app_config):
    hooked_module = {}
    module = None

    for (m, do_log) in HOOK_SUPPORT_LIST:
        try:
            module = _is_module_exist(m)
        except Exception as e:
            _log('ERROR', 'check-module-loaded', e, 'at', __name__)
            import traceback
            for line in traceback.format_stack():
                _log('ERROR', 'callstack', line.strip())
            continue

        try:
            if __current_python_ver__ < m.__minimum_python_version__:
                continue

            if module is not False:
                if app_config.skip_module is not None:
                    if module.__name__ in app_config.skip_module:
                        _log('INFO', 'skip module', module.__name__)
                        continue

                if m.hook(module) is True:
                    hooked_module[m.__hooking_module__] = {'target_module': module, 'hook_module': m,
                                                           'version': m.get_target_version()}
                    if do_log:
                        agent_obj.log_to_file('module name:' + module.__name__)
        except Exception as e:
            _diag_log('ERROR', 'hooking:', module, '(' + m.__hooking_module__ + ')', e)

    global __hooked_module__
    __hooked_module__ = hooked_module
    _hook_builtins()


def _unhook_builtins():
    global _original_builtins_open
    global _original_builtins_print
    global _original_builtins_socket_connect
    global _original_builtins_socket_connect_ex

    try:
        import socket
        if _original_builtins_open is not None:
            __builtins__['open'] = _original_builtins_open

        if _original_builtins_print is not None:
            __builtins__['print'] = _original_builtins_print

        if _original_builtins_socket_connect is not None:
            socket.socket.connect = _original_builtins_socket_connect

        if _original_builtins_socket_connect_ex is not None:
            socket.socket.connect_ex = _original_builtins_socket_connect_ex
    except Exception as e:
        _log( 'ERROR', '_hook_builtins', e)


# Socket Open/Connect 가로채기
def _hook_builtins():
    global _original_builtins_open
    global _original_builtins_print
    global _original_builtins_socket_connect
    global _original_builtins_socket_connect_ex

    try:
        import socket

        _original_builtins_open = __builtins__['open']
        __builtins__['open'] = _wrap_file_open(__builtins__['open'])

        if os.getenv('JENNIFER_PROFILE_PRINT'):
            _original_builtins_print = __builtins__['print']
            __builtins__['print'] = _wrap_file_print(__builtins__['print'])

        _original_builtins_socket_connect = socket.socket.connect
        socket.socket.connect = _wrap_socket_connect(socket.socket.connect)

        _original_builtins_socket_connect_ex = socket.socket.connect_ex
        socket.socket.connect_ex = _wrap_socket_connect(socket.socket.connect_ex)
    except Exception as e:
        _log('ERROR', '_hook_builtins', e)


def _wrap_file_print(origin_print):
    def _handler(*args, **kwargs):
        try:
            agent = jennifer_agent()
            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    text = ' '.join(map(str, args))
                    o.profiler.add_message(text)
        except:
            pass

        return origin_print(*args, **kwargs)

    return _handler


def _wrap_file_open(origin_open):
    def _handler(file_path, mode='r', *args, **kwargs):
        try:
            agent = jennifer_agent()
            transaction = agent.current_active_object()

            if transaction is not None and 'site-packages' not in file_path:
                transaction.profiler.add_file_profile(
                    name=os.path.abspath(os.path.join(os.getcwd(), file_path)),
                    mode=mode
                )
        except:
            pass

        return origin_open(file_path, mode, *args, **kwargs)

    return _handler


def _wrap_socket_connect(origin_connect):
    import socket

    def add_socket_profile(this_self, o):
        if this_self.family != socket.AF_INET:
            return

        if o is not None:
            remote_address = this_self.getpeername()
            local_address = this_self.getsockname()
            o.profiler.add_socket_profile(
                host=remote_address[0],
                port=remote_address[1],
                local=local_address[1],
            )

    def add_async_socket_profile(this_self, o, target_address):
        if this_self.family != socket.AF_INET:
            return

        if o is not None:
            o.profiler.add_message('[async-socket-connect] ' + str(target_address))

    def _handler(self, address):
        agent = jennifer_agent()
        o = agent.current_active_object()

        try:
            ret = origin_connect(self, address)
            add_socket_profile(self, o)
            return ret
        except BlockingIOError:
            add_async_socket_profile(self, o, address)
            raise
        except Exception as e:
            if o is not None:
                err_msg = str(e) + ' ' + str(address)
                o.profiler.profile_exception_event(ERROR_TYPE_EXTERNAL_CALL_EXCEPTION, err_msg)
            raise

    return _handler
