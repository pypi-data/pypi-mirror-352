from jennifer.api.proxy import Proxy
from jennifer.agent import jennifer_agent
from jennifer.protocol.remote_call import *
import json
from .util import VersionInfo

__hooking_module__ = 'pymongo'
__minimum_python_version__ = VersionInfo("2.7.0")
_mongo_client_origin = None
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


class CollectionProxy(Proxy):
    def __init__(self, obj, host, port, name):
        Proxy.__init__(self, obj)
        self.set('collection', name)
        self.set('host', str(host))
        self.set('port', port)
        self.set('call_info', create_remote_ip_port_capturing_call(REMOTE_CALL_TYPE_MONGODB, host, port))

    def with_options(self, *args, **kwargs):
        obj = self._origin.with_options(*args, **kwargs)
        return CollectionProxy(obj, self.host, self.port, self.collection)

    def find(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    parameter = None
                    document = _safe_get(args, 0)
                    try:
                        parameter = json.dumps(document)
                    except:
                        parameter = "..."

                    pi = o.profiler.start_query(self.call_info, self.collection + '.find(' + parameter + ')',
                                                self.host, self.port)
        except Exception as e:
            pass

        result = None
        err = None

        try:
            result = self._origin.find(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result

    def find_one_and_replace(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    parameter = None
                    filter_ = _safe_get(args, 0) or kwargs.get('filter')
                    replacement = _safe_get(args, 1) or kwargs.get('replacement')

                    try:
                        parameter = [json.dumps(filter_), json.dumps(replacement)]
                    except:
                        parameter = "..."

                    pi = o.profiler.start_query(self.call_info,
                                                self.collection +
                                                '.find_one_and_replace(' + parameter[0] + ', ' + parameter[1] + ')',
                                                self.host, self.port)
        except:
            pass

        err = None
        result = None

        try:
            result = self._origin.find_one_and_replace(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result

    def insert_many(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    parameter = None
                    document = _safe_get(args, 0) or kwargs.get('documents')
                    try:
                        parameter = json.dumps(document)
                    except:
                        parameter = "..."

                    pi = o.profiler.start_query(self.call_info,
                                                self.collection + ".insert_many(" + parameter + ")",
                                                self.host, self.port)
        except:
            pass

        result = None
        err = None

        try:
            result = self._origin.insert_many(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result

    def update_many(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    filter_expression = _safe_get(args, 0) or kwargs.get('filter')
                    update_expression = _safe_get(args, 1) or kwargs.get('update')

                    try:
                        parameter = json.dumps(filter_expression)
                        parameter = parameter + ", " + json.dumps(update_expression)
                    except:
                        parameter = "..."

                    pi = o.profiler.start_query(self.call_info,
                                                self.collection + ".update_many(" + parameter + ")",
                                                self.host, self.port)
        except:
            pass

        result = None
        err = None

        try:
            result = self._origin.update_many(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result

    def update_one(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    filter_expression = _safe_get(args, 0) or kwargs.get('filter')
                    update_expression = _safe_get(args, 1) or kwargs.get('update')

                    try:
                        parameter = json.dumps(filter_expression)
                        parameter = parameter + ", " + json.dumps(update_expression)
                    except:
                        parameter = "..."

                    pi = o.profiler.start_query(self.call_info,
                                                self.collection + ".update_one(" + parameter + ")",
                                                self.host, self.port)
        except:
            pass

        result = None
        err = None

        try:
            result = self._origin.update_one(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result

    def insert_one(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    parameter = None
                    document = _safe_get(args, 0) or kwargs.get('document')

                    try:
                        parameter = json.dumps(document)
                    except:
                        parameter = "..."

                    pi = o.profiler.start_query(self.call_info,
                                                self.collection + ".insert_one(" + parameter + ")",
                                                self.host, self.port)
        except:
            pass

        result = None
        err = None

        try:
            result = self._origin.insert_one(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result

    def delete_many(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    parameter = None
                    document = _safe_get(args, 0) or kwargs.get('filter')

                    try:
                        parameter = json.dumps(document)
                    except:
                        parameter = "..."

                    pi = o.profiler.start_query(self.call_info,
                                                self.collection + ".delete_many(" + parameter + ")",
                                                self.host, self.port)
        except:
            pass

        result = None
        err = None

        try:
            result = self._origin.delete_many(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result


class DatabaseProxy(Proxy):
    def __init__(self, obj, host, port, name):
        Proxy.__init__(self, obj)
        self.set('db', name)

        origin_getitem = self._origin.__getitem__

        def getitem(key_name):
            collection = origin_getitem(key_name)

            if isinstance(collection, CollectionProxy):
                return collection
            else:
                return CollectionProxy(collection, host, port, self.db + '.' + key_name)

        self._origin.__getitem__ = getitem


def unhook(pymongo_module):
    global _mongo_client_origin
    if _mongo_client_origin is None:
        return
    pymongo_module.MongoClient = _mongo_client_origin


def hook(pymongo_module):
    global _mongo_client_origin

    if 'MongoClientWrap' in str(pymongo_module.MongoClient):
        return False

    _mongo_client_origin = pymongo_module.MongoClient

    class MongoClientWrap3(_mongo_client_origin):
        def __init__(*args, **kwargs):
            _mongo_client_origin.__init__(*args, **kwargs)

        def __getitem__(self, name):
            database = _mongo_client_origin.__getitem__(self, name)
            host, port = self.address
            return DatabaseProxy(database, host, port, name)

        def get_database(*args, **kwargs):
            database = _mongo_client_origin.get_database(*args, **kwargs)

            myself = _safe_get(args, 0)
            name = _safe_get(args, 1) or kwargs.get('name')

            host, port = myself.address
            return DatabaseProxy(database, host, port, name)

    class MongoClientWrap4(_mongo_client_origin):
        def __init__(*args, **kwargs):
            _mongo_client_origin.__init__(*args, **kwargs)

            myself = _safe_get(args, 0)
            myself.__host = _safe_get(args, 1) or kwargs.get('host') or '127.0.0.1'
            myself.__port = _safe_get(args, 2) or kwargs.get('port') or 27017

        def __getitem__(self, name):
            database = _mongo_client_origin.__getitem__(self, name)
            return DatabaseProxy(database, self.__host, self.__port, name)

        def get_database(*args, **kwargs):
            database = _mongo_client_origin.get_database(*args, **kwargs)

            myself = _safe_get(args, 0)
            name = _safe_get(args, 1) or kwargs.get('name')
            return DatabaseProxy(database, myself.__host, myself.__port, name)

    global __target_version
    __target_version = pymongo_module.__version__
    current_ver = VersionInfo(__target_version)
    base_ver = VersionInfo("3.12.3")

    if current_ver <= base_ver:
        pymongo_module.MongoClient = MongoClientWrap3
    else:
        pymongo_module.MongoClient = MongoClientWrap4

    return True
