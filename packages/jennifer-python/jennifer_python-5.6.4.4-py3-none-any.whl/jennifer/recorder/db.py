
import jennifer.api.proxy


class DBConnectionRecorder(object):
    def __init__(self):
        self.connections = {}

    def add_connection(self, conn):
        self.connections[conn] = 0

    def remove_connection(self, conn):
        try:
            self.connections.pop(conn)
            return True
        except KeyError:
            return False

    def active(self, conn):
        if isinstance(conn, jennifer.wrap.db_api.CursorProxy):
            current_connection = conn.conn
        elif isinstance(conn, jennifer.wrap.db_api.ConnectionProxy):
            current_connection = conn
        else:
            return

        self.connections[current_connection] = 1

    def inactive(self, conn):
        if isinstance(conn, jennifer.wrap.db_api.CursorProxy):
            current_connection = conn.conn
        elif isinstance(conn, jennifer.wrap.db_api.ConnectionProxy):
            current_connection = conn
        else:
            return

        self.connections[current_connection] = 0

    def record(self):
        active = 0
        values = self.connections.values()
        for v in values:
            active += v

        return (
            len(self.connections),  # total
            active,  # active
        )
