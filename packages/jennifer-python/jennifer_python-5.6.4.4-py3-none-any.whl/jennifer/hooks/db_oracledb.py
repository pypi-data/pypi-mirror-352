from jennifer.pconstants import *
from .util import VersionInfo

# python-oracledb
# https://oracle.github.io/python-oracledb/
__hooking_module__ = 'oracledb'
__minimum_python_version__ = VersionInfo("3.8.0")
__target_version = None

_original_db_connect = None
_original_db_connect_async = None


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


_dsn_cache = {}


def parse_dsn(text):
    if text is None:
        return ""

    if _dsn_cache.get(text, None) is not None:
        return _dsn_cache[text]

    # remove white space
    text = text.replace(" ", "")

    # ignore multiple address
    # get ip and port from oracle dsn string
    # ex) ""(DESCRIPTION=
    #                  (ADDRESS=(PROTOCOL=tcp)(HOST=192.168.100.50)(PORT=1521))
    #                  (CONNECT_DATA=(SERVICE_NAME=XE)))"""

    host = get_dsn_value(text, "HOST")
    port = get_dsn_value(text, "PORT")
    service_name = get_dsn_value(text, "SERVICE_NAME")

    if service_name == '':
        _dsn_cache[text] = host + ":" + port
    else:
        _dsn_cache[text] = host + ":" + port + "/" + service_name

    return _dsn_cache[text]


def get_dsn_value(text, key_name):
    found = text.find(key_name + "=")
    if found != -1:
        text = text[found + len(key_name) + 1:]
        found = text.find(")")
        if found != -1:
            return text[:found]

    return ''


def connection_info(*args, **kwargs):
    try:
        dsn = kwargs.get('dsn') or None
        if dsn is None:
            return '(None)', 1521, '', None

        desc_text = get_dsn_value(dsn, "DESCRIPTION")
        if desc_text == '':
            host, port, service_name = get_host_and_service_name(dsn)
        else:
            ip_port_service = parse_dsn(dsn)
            host, port, service_name = get_host_and_service_name(ip_port_service)

        return host, port, service_name, None
    except Exception as e:
        return '(None)', 1521, '', None


def get_host_and_service_name(dsn_text):
    found = dsn_text.find('/')
    if found == -1:
        host, port = get_host_and_port(dsn_text)
        return host, port, ''

    host, port = get_host_and_port(dsn_text[:found])
    return host, port, dsn_text[found + 1:]


def get_host_and_port(text):
    found = text.find(':')
    if found == -1:
        return text, 1521

    return text[:found], int(text[found + 1:])


def unhook(oracledb_module):
    global _original_db_connect
    if _original_db_connect is not None:
        oracledb_module.connect = _original_db_connect


def hook(oracledb_module):
    from jennifer.wrap import db_api

    global __target_version
    __target_version = oracledb_module.__version__

    global _original_db_connect
    if 'register_database.' in str(oracledb_module.connect):
        return False

    _original_db_connect = db_api.register_database(oracledb_module, REMOTE_CALL_TYPE_ORACLE, connection_info)

    # https://python-oracledb.readthedocs.io/en/v2.4.1/api_manual/async_connection.html
    # if __target_version is not None:
    #     module_version = VersionInfo(__target_version)
    #     async_support_version = VersionInfo("2.4.0")
    #
    #     if module_version < async_support_version:
    #         return True
    #
    #     global _original_db_connect_async
    #     if 'register_database_async.' in str(oracledb_module.connect_async):
    #         return False
    #
    #     _original_db_connect_async = db_api.register_database_async(oracledb_module, REMOTE_CALL_TYPE_ORACLE, connection_info)

    return True
