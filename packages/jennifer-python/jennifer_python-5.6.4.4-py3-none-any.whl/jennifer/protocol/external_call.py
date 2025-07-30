# -*- coding: utf-8 -*-

from .profile_data import PiData


class PiExternalCall(PiData):
    def __init__(self, o, call_type, host, port, text_hash):
        PiData.__init__(self, o)

        self.type = PiData.TYPE_EXTERNAL_CALL
        self.text_hash = text_hash
        self.end_time = 0
        self.end_cpu = 0

        # proxy로 넘어간 후 처리되는 데이터
        self.host = host
        self.port = port

        self.call_type = call_type
        self.desc_hash = text_hash
        self.error_hash = 0

        self.outgoing_remote_call = None

    def to_json(self):
        ret = self.__dict__

        if self.outgoing_remote_call is not None:
            ret['outgoing_remote_call'] = self.outgoing_remote_call.to_dict()

        return ret

    def get_type(self):
        return self.type
