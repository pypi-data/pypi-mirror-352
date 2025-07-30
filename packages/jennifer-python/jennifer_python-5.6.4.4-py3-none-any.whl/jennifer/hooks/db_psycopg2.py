import os
from jennifer.pconstants import *
from .util import VersionInfo

__hooking_module__ = 'psycopg2'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_db_connect = None
_original_extensions_register_type = None
_original_psycopg_register_type = None
_original_json_register_type = None
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


def _connection_info(*args, **kwargs):
    host = kwargs.get('host')
    port = kwargs.get('port') or 5432
    database = kwargs.get('dbname')

    try:
        if host is None:
            connection_string = _safe_get(args, 0)
            host, port, database = _get_db_info_from_string(connection_string)
    except:
        pass

    return host, port, database, None


def _get_db_info_from_string(text):
    key_value = dict(item.split('=') for item in text.split(' '))

    port = 5432
    if key_value['port'] is not None:
        port = int(key_value['port'])

    return key_value['host'], port, key_value['dbname']


def _unwrap_register_type_args(obj, scope=None):
    return obj, scope


def _wrap_register_type(register_type_func):

    def handler(*args, **kwargs):
        try:
            from jennifer.wrap import db_api

            obj, scope = _unwrap_register_type_args(*args, **kwargs)

            if scope and isinstance(scope, db_api.Proxy):
                scope = scope._origin

            return register_type_func(obj, scope)
        except:
            return register_type_func(*args, **kwargs)

    return handler


def unhook(psycopg2_module):
    global _original_db_connect
    global _original_extensions_register_type
    global _original_psycopg_register_type
    global _original_json_register_type

    if _original_db_connect is not None:
        psycopg2_module.connect = _original_db_connect

    if _original_extensions_register_type is not None:
        psycopg2_module.extensions.register_type = _original_extensions_register_type

    if _original_psycopg_register_type is not None:
        psycopg2_module._psycopg.register_type = _original_psycopg_register_type

    if _original_json_register_type is not None:
        psycopg2_module._json.register_type = _original_json_register_type


def hook(psycopg2_module):
    from jennifer.wrap import db_api

    global __target_version
    __target_version = psycopg2_module.__version__

    global _original_db_connect
    _original_db_connect = db_api.register_database(psycopg2_module, REMOTE_CALL_TYPE_POSTGRESQL, _connection_info)

    global _original_extensions_register_type
    global _original_psycopg_register_type

    if '_wrap_register_type.' in str(psycopg2_module.extensions.register_type):
        return False

    _original_extensions_register_type = psycopg2_module.extensions.register_type
    _original_psycopg_register_type = psycopg2_module._psycopg.register_type

    psycopg2_module.extensions.register_type = _wrap_register_type(psycopg2_module.extensions.register_type)
    psycopg2_module._psycopg.register_type = _wrap_register_type(psycopg2_module._psycopg.register_type)

    current_ver = VersionInfo(__target_version)
    base_ver = VersionInfo("2.5.0")

    if current_ver >= base_ver:
        global _original_json_register_type
        _original_json_register_type = psycopg2_module._json.register_type
        psycopg2_module._json.register_type = _wrap_register_type(psycopg2_module._json.register_type)

    return True
