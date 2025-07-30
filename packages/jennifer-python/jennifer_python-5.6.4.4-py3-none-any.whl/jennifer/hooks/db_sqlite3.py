from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'sqlite3'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_db_connect = None
_original_dbapi2_connect = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    return __import__(__hooking_module__)


def connection_info(database, *args, **kwargs):
    return 'localhost', 0, database, None


def unhook(sqlite3_module):
    global _original_db_connect
    if _original_db_connect is not None:
        sqlite3_module.connect = _original_db_connect

    global _original_dbapi2_connect
    if _original_dbapi2_connect is not None:
        sqlite3_module.dbapi2.connect = _original_dbapi2_connect


def hook(sqlite3_module):
    from jennifer.wrap import db_api

    global __target_version
    __target_version = sqlite3_module.version

    global _original_db_connect
    if 'register_database.' in str(sqlite3_module.connect):
        return False

    _original_db_connect = db_api.register_database(sqlite3_module, REMOTE_CALL_TYPE_SQLITE, connection_info)

    if sqlite3_module.dbapi2 is not None:
        global _original_dbapi2_connect
        __target_version = __target_version + '(dbapi2)'
        _original_dbapi2_connect = db_api.register_database(sqlite3_module.dbapi2,
                                                            REMOTE_CALL_TYPE_SQLITE, connection_info)
    return True
