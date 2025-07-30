import time


class PiData:
    TYPE_EMPTY = 0
    TYPE_METHOD = 0x10
    TYPE_EXTERNAL_CALL = 0x20
    TYPE_SQL_EXEC = 0x30
    TYPE_SQL_FETCH = 0x40
    TYPE_MESSAGE = 0x50
    TYPE_DB_MESSAGE = 0x60
    TYPE_FILE = 8 << 4
    TYPE_SOCKET = 9 << 4
    TYPE_EXCEPTION = 10 << 4
    TYPE_METHOD_PARAM = 13 << 4
    TYPE_METHOD_RETURN = 14 << 4
    TYPE_ERROR = 1

    def __init__(self, o):
        self.type = PiData.TYPE_EMPTY
        self.start_time = o.get_current_point_time()
        self.start_cpu = o.get_end_of_cpu_time()

        self.index = 0
        self.parent_index = 0

    def get_type(self):
        return self.type

    def to_json(self):
        ret = self.__dict__
        ret['type'] = self.get_type()
        return ret
