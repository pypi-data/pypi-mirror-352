from .profile_data import PiData


class PiDBMessage(PiData):

    def __init__(self, o, message_type, message):
        PiData.__init__(self, o)

        self.type = PiData.TYPE_DB_MESSAGE
        self.message = message
        self.message_type = message_type
        self.end_time = 0
        self.end_cpu = 0

    def get_type(self):
        return self.type
