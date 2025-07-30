from .profile_data import PiData


class PiMessage(PiData):
    def __init__(self, o, message):
        PiData.__init__(self, o)
        self.type = PiData.TYPE_MESSAGE
        self.message = message
        self.time = 0

    def get_type(self):
        return self.type

    def print_description(self):
        print(' ' * (self.parent_index + 4), 'Message', self.parent_index, self.index, self.message)
