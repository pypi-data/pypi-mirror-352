from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'MySQLdb'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_db_connect = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    return __import__(__hooking_module__)


def safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def connection_info(*args, **kwargs):
    host = safe_get(args, 0) or kwargs.get('host')
    port = safe_get(args, 6) or kwargs.get('port') or 3306
    database = safe_get(args, 4) or kwargs.get('database') or kwargs.get('db')
    return host, port, database, None


def unhook(my_sql_db):
    global _original_db_connect
    if _original_db_connect is not None:
        my_sql_db.connect = _original_db_connect


def hook(my_sql_db):
    from jennifer.wrap import db_api

    global __target_version
    __target_version = my_sql_db.version_info

    global _original_db_connect
    if 'register_database.' in str(my_sql_db.connect):
        return False

    _original_db_connect = db_api.register_database(my_sql_db, REMOTE_CALL_TYPE_MYSQL, connection_info)
    return True

