# -*- coding: utf8 -*-
from jennifer.agent import jennifer_agent
from jennifer.api.proxy import Proxy
import jennifer.protocol.remote_call as remote_call


def _safe_get(attr, idx, default=None):
    try:
        return attr[idx]
    except IndexError:
        return default


class CursorProxy(Proxy):
    __slots__ = '__fetch_count__'

    def __init__(self, obj, host, port, paramstyle, conn, db_type):

        Proxy.__init__(self, obj)
        self.set('host', host)
        self.set('port', port)
        self.set('paramstyle', paramstyle)
        self.set('conn', conn)
        self.set('__fetch_count__', 0)
        self.set('db_type', db_type)
        self.set('call_info', remote_call.create_remote_ip_port_capturing_call(db_type, host, port))

    def __enter__(self, *args, **kwargs):
        origin_cursor = Proxy.__enter__(self, *args, **kwargs)
        return CursorProxy(origin_cursor, self.host, self.port, self.paramstyle, self, self.db_type)

    def __exit__(self, *args, **kwargs):
        o = None

        try:
            agent = jennifer_agent()
            if agent is not None:
                removed = agent.recorder.db_recorder.remove_connection(self.conn)
                o = agent.current_active_object()
                if o is not None and removed:
                    o.profiler.db_close()
        except:
            pass

        try:
            Proxy.__exit__(self, *args, **kwargs)
        except Exception as e:
            if o is not None:
                o.profiler.end()
            raise e

        try:
            if o is not None:
                o.profiler.end()
        except:
            pass

        return

    # 변경 시 CursorProxy의 ConnectionProxy도 함께 변경
    def execute(self, *args, **kwargs):
        o = None
        agent = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

            operation = _safe_get(args, 0) or kwargs.get('operation')
            parameters = _safe_get(args, 1) or kwargs.get('parameters')

            if self.paramstyle == 'qmark':
                parameters = args[1:]

            if o is not None and operation is not None:
                agent.recorder.db_recorder.active(self.conn)
                pi = o.profiler.start_query(self.call_info, operation, self.host, self.port,
                                            parameters, self.paramstyle)
        except Exception as e:
            pass

        result = None
        err = None
        try:
            result = self._origin.execute(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                agent.recorder.db_recorder.inactive(self)
                o.profiler.end_query(pi, err)
        except Exception as e:
            pass

        if err is not None:
            raise err

        return result

    def process_fetch(self, fetch, size, pass_size=False, is_fetch_one=False):
        o = None
        args = []
        agent = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()
                if o is not None:
                    agent.recorder.db_recorder.active(self.conn)
                    pi = o.profiler.start_db_fetch(o)

            if pass_size:
                args = [size]
        except Exception as e:
            pass

        if pi is None:
            return fetch(*args)

        err = None
        ret = None

        try:
            ret = fetch(*args)
        except Exception as e:
            err = e

        try:
            if ret is not None:
                if is_fetch_one is True:
                    current_count = self.get('__fetch_count__')
                    self.set('__fetch_count__', current_count + 1)
                else:
                    o.profiler.end_db_fetch(pi, o, len(ret))
            else:
                fetch_count = self.get('__fetch_count__')
                if fetch_count is not None and fetch_count != 0:
                    o.profiler.end_db_fetch(pi, o, fetch_count)

            agent.recorder.db_recorder.inactive(self.conn)
        except:
            pass

        if err is not None:
            raise err

        return ret

    def fetchone(self):
        return self.process_fetch(self._origin.fetchone, 1, is_fetch_one=True)

    def fetchmany(self, size=None):
        pass_size = True
        if size is None:
            size = self._origin.arraysize
            pass_size = False
        return self.process_fetch(self._origin.fetchmany, size, pass_size)

    def fetchall(self):
        size = self.rowcount
        return self.process_fetch(self._origin.fetchall, size)

    def close(self):
        self._origin.close()


class ConnectionProxy(Proxy):

    def __init__(self, obj_connection, db_type, host, port, paramstyle):
        Proxy.__init__(self, obj_connection)
        self.set('host', host)
        self.set('port', port)
        self.set('paramstyle', paramstyle)
        self.set('db_type', db_type)
        self.set('call_info', remote_call.create_remote_ip_port_capturing_call(db_type, host, port))

    def cursor(self, *args, **kwargs):
        return CursorProxy(self._origin.cursor(*args, **kwargs),
                           self.host, self.port, self.paramstyle, self, self.db_type)

    # 변경 시 CursorProxy의 execute도 함께 변경
    def query(self, *args, **kwargs):
        o = None
        agent = None
        pi = None

        try:
            agent = jennifer_agent()

            if agent is not None:
                o = agent.current_active_object()

            operation = _safe_get(args, 0) or kwargs.get('operation')
            parameters = _safe_get(args, 1) or kwargs.get('parameters')

            if o is not None and operation is not None:
                agent.recorder.db_recorder.active(self)
                pi = o.profiler.start_query(self.call_info, operation, self.host, self.port, parameters,
                                            self.paramstyle)
        except:
            pass

        result = None
        err = None
        try:
            result = self._origin.query(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                agent.recorder.db_recorder.inactive(self)
                o.profiler.end_query(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return result

    def __enter__(self, *args, **kwargs):
        origin_connection = Proxy.__enter__(self, *args, **kwargs)

        host = self.get('host')
        port = self.get('port')
        db_type = self.get('db_type')
        paramstyle = self.get('paramstyle')

        connection = ConnectionProxy(origin_connection, db_type, host, port, paramstyle)
        return connection

    def __exit__(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()
            removed = agent.recorder.db_recorder.remove_connection(self)
            if removed:
                o = agent.current_active_object()
                pi = o.profiler.start_conn_close()
        except:
            pass

        err = None
        try:
            Proxy.__exit__(self, *args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_conn_close(pi)
        except:
            pass

        if err is not None:
            raise err

        return

    def close(self, *args, **kwargs):
        o = None
        pi = None

        try:
            agent = jennifer_agent()
            removed = agent.recorder.db_recorder.remove_connection(self)
            if removed:
                o = agent.current_active_object()
                pi = o.profiler.start_conn_close()
        except:
            pass

        err = None
        try:
            self._origin.close(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_conn_close(pi)
        except:
            pass

        if err is not None:
            raise err

        return


def register_database(db_module, db_type, connection_info):
    def _wrap_connect(connect):

        def handler(*args, **kwargs):
            agent = jennifer_agent()

            o = None
            host = None
            port = 0
            pi = None
            connection = None
            current_db_type = db_type

            try:
                if agent.app_config.enable_sql_trace is not True:
                    return connect(*args, **kwargs)

                host, port, database, selected_db_type = connection_info(*args, **kwargs)
                if selected_db_type is not None:
                    current_db_type = selected_db_type

                o = agent.current_active_object()

                if o is not None:
                    pi = o.profiler.start_conn_open(host, port, database)
            except:
                pass

            err = None
            try:
                origin_connection = connect(*args, **kwargs)
                if isinstance(origin_connection, ConnectionProxy):
                    connection = origin_connection
                else:
                    if o is not None:
                        connection = ConnectionProxy(origin_connection, current_db_type, host, port, db_module.paramstyle)
                    else:
                        connection = origin_connection
            except Exception as e:
                err = e

            try:
                if pi is not None:
                    o.profiler.end_conn_open(pi, err)
                    agent.recorder.db_recorder.add_connection(connection)
            except:
                pass

            if err is not None:
                raise err

            return connection

        return handler

    original_connect = db_module.connect
    db_module.connect = _wrap_connect(db_module.connect)
    return original_connect


def register_database_async(db_module, db_type, connection_info):
    def _wrap_connect_async(connect_async):

        async def handler(*args, **kwargs):
            agent = jennifer_agent()

            o = None
            host = None
            port = 0
            pi = None
            connection = None
            current_db_type = db_type

            try:
                if agent.app_config.enable_sql_trace is not True:
                    return await connect_async(*args, **kwargs)

                host, port, database, selected_db_type = connection_info(*args, **kwargs)
                if selected_db_type is not None:
                    current_db_type = selected_db_type

                o = agent.current_active_object()

                if o is not None:
                    pi = o.profiler.start_conn_open(host, port, database)
            except:
                pass

            err = None
            try:
                origin_connection = await connect_async(*args, **kwargs)

                if o is not None:
                    connection = ConnectionProxy(origin_connection, current_db_type, host, port, db_module.paramstyle)
                else:
                    connection = origin_connection
            except Exception as e:
                err = e

            try:
                if pi is not None:
                    o.profiler.end_conn_open(pi, err)
                    agent.recorder.db_recorder.add_connection(connection)
            except:
                pass

            if err is not None:
                raise err

            return connection

        return handler

    original_connect_async = db_module.connect_async
    db_module.connect_async = _wrap_connect_async(db_module.connect_async)
    return original_connect_async
