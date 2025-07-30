from .profile_data import PiData


class PiSocket(PiData):
    TYPE_IOSTREAM = 7

    def __init__(self, o, host, port, local_port):
        PiData.__init__(self, o)
        self.type = PiData.TYPE_SOCKET
        self.host = host
        self.port = port
        self.local_port = local_port
        self.mode = PiSocket.TYPE_IOSTREAM

    def get_type(self):
        return self.type
