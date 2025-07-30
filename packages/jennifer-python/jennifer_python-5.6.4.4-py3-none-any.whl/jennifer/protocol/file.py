from .profile_data import PiData


class PiFile(PiData):
    FILE_TYPE_UNKNOWN = 0
    FILE_TYPE_READ = 1
    FILE_TYPE_WRITE = 2
    FILE_TYPE_RWOPEN = 6

    def __init__(self, o, name='', mode=''):
        PiData.__init__(self, o)
        self.name = name
        self.type = PiData.TYPE_FILE
        is_read = 'r' in mode
        is_write = 'w' in mode

        self.mode = PiFile.FILE_TYPE_UNKNOWN
        if is_read and is_write:
            self.mode = PiFile.FILE_TYPE_RWOPEN
        elif is_read:
            self.mode = PiFile.FILE_TYPE_READ
        elif is_write:
            self.mode = PiFile.FILE_TYPE_WRITE

    def get_type(self):
        return self.type
