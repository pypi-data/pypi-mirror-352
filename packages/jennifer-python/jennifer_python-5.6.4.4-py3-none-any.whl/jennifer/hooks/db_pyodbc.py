from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'pyodbc'
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
    host = "(unknown)"
    port = 0
    database = "(unknown)"

    if len(args) == 1:
        addr = _safe_get(args, 0)

        db_type, host, database = get_info_from_addr(addr)
        if host is None:
            return host, port, database, None

        port = kwargs.get('port') or 0
        if port == 0:
            if db_type == REMOTE_CALL_TYPE_MSSQL:
                port = 1433

    return host, port, database, db_type


def get_info_from_addr(connection_string):
    db_type, host, database = REMOTE_CALL_TYPE_UNKNOWN_SQL_DATABASE, "(unknown)", "(unknown)"

    for key_value in connection_string.split(';'):
        item = key_value.split('=')
        if len(item) != 2:
            continue

        key = item[0].strip().lower()
        value = item[1].strip()

        if key == 'driver':
            if value.lower().find('sql server') >= 0:
                db_type = REMOTE_CALL_TYPE_MSSQL

        if key == 'server':
            host = item[1]

        if key == 'database':
            database = item[1]

    return db_type, host, database


def unhook(odbc_db_module):
    global _original_db_connect
    if _original_db_connect is not None:
        odbc_db_module.connect = _original_db_connect


def hook(odbc_db_module):
    from jennifer.wrap import db_api

    global __target_version
    __target_version = odbc_db_module.version

    global _original_db_connect
    if 'register_database.' in str(odbc_db_module.connect):
        return False

    _original_db_connect = db_api.register_database(odbc_db_module,
                                                    REMOTE_CALL_TYPE_UNKNOWN_SQL_DATABASE, connection_info)
    return True
