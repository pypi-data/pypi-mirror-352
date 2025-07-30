from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'pymssql'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_db_connect = None
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


def connection_info(*args, **kwargs):
    host = _safe_get(args, 0) or kwargs.get('server')
    if host is None:
        host = _safe_get(args, 8) or kwargs.get('host') or 'localhost'

    port = _safe_get(args, 10) or kwargs.get('port') or 1433
    database = _safe_get(args, 3) or kwargs.get('database') or ''
    return host, port, database, None


def unhook(mssql_db):
    global _original_db_connect
    if _original_db_connect is not None:
        mssql_db.connect = _original_db_connect


def hook(mssql_db):
    from jennifer.wrap import db_api

    global __target_version
    __target_version = mssql_db.VERSION

    global _original_db_connect
    if 'register_database.' in str(mssql_db.connect):
        return False

    _original_db_connect = db_api.register_database(mssql_db, REMOTE_CALL_TYPE_MSSQL, connection_info)
    return True
