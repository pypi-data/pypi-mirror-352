# -*- coding: utf-8 -*-

from .profile_data import PiData
from jennifer.pconstants import *


class PiSql(PiData):
    def __init__(self, o, query_hash, query, params, query_format, host, port, call_info):
        PiData.__init__(self, o)

        self.active_object = o
        self.type = PiData.TYPE_SQL_EXEC

        self.end_time = 0
        self.end_cpu = 0

        self.is_sync = True
        self.method_type = SQL_DEF_PSTMT_EXE_QRY
        self.key = query_hash

        self.outgoing_remote_call = call_info

        self.dbc = 0
        self.sherpaOracleSequence = 0
        self.sherpaOracleInstanceName = ''

        self.dataSourceOrConnectionName = None

        # 아래의 필드는 Proxy 측에서 사용
        self.query = query
        self.params = params
        self.query_format = query_format
        self.port = port
        self.host = host
        self.error_hash = 0

    def to_json(self):
        ret = self.__dict__

        ret.pop('active_object', None)
        ret['outgoing_remote_call'] = self.outgoing_remote_call.to_dict()

        return ret

    def get_type(self):
        return self.type
