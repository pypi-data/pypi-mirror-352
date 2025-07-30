import threading
import os
import sys
import platform
from .util import VersionInfo

cached_agent = {}
fastapi_ctx = None

is_async = False

__current_python_ver__ = VersionInfo(platform.python_version())
python33_version = VersionInfo("3.3.0")
python30_version = VersionInfo("3.0.0")

use_get_ident = __current_python_ver__ >= python33_version
version_python30_below = __current_python_ver__ < python30_version

hook_lock = threading.Lock()

if os.getenv('JENNIFER_IS_ASYNC') is not None:
    is_async = bool(os.environ['JENNIFER_IS_ASYNC'])


def is_python30_below():
    return version_python30_below


def jennifer_agent():
    global cached_agent

    process_id = os.getpid()

    if process_id not in cached_agent.keys():

        from .agent import Agent
        from jennifer.hooks import hooking, unhooking
        from .util import _diag_log

        if is_async:
            local_agent = Agent(_get_temp_id, is_async)
        else:
            local_agent = Agent(_current_thread_id, is_async)

        cached_agent[process_id] = local_agent

        _diag_log("INFO", "[ppid: " + str(os.getppid()) + "]", "sys.path: " + str(sys.path), ', (', sys.version, ')' )
        if local_agent.initialize_agent() is False:
            cached_agent[process_id] = None
            return None

        with hook_lock:
            hooking(local_agent, local_agent.app_config)

    return cached_agent[process_id]


def _current_thread_id():
    if use_get_ident:
        return threading.get_ident()  # python 3.3 or later
    else:
        return threading.current_thread().ident


def _get_temp_id():
    return 0
