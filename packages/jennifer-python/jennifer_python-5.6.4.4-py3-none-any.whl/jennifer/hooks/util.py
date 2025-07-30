# -*- coding: utf-8 -*-

import os
from datetime import datetime
import traceback

enable_diagnostics = os.getenv('JENNIFER_DBG') == '1'
diagnostics_to_file = os.getenv('JENNIFER_LOG_FILE') or None


def format_time(time_value):
    return time_value.strftime("[%Y-%m-%d %H:%M:%S]")


def _log_tb(*args):
    current_time = format_time(datetime.now())
    print(current_time, '[' + str(os.getpid()) + ']', 'ERROR', '[jennifer]', args)
    traceback.print_exc()


def _log(level, *args):
    current_time = format_time(datetime.now())
    print(current_time, '[' + str(os.getpid()) + ']', level, '[jennifer]', args)


def _diag_log(level, *args):
    if enable_diagnostics is False:
        return

    time_now = datetime.now()
    time_column = format_time(time_now)

    print(time_column, '[' + str(os.getpid()) + ']', level, '[jennifer]', args)

    if diagnostics_to_file is not None:
        log_file_path = os.path.join(diagnostics_to_file, "agent_diag_" + str(os.getpid()) + ".log")
        with open(log_file_path, 'a') as log_file:
            log_file.write(time_column + ' ' + str(args) + '\n')


class VersionInfo(object):
    def __init__(self, version_string):
        self.text = version_string
        self.major = 0
        self.minor = 0
        self.revision = 0
        self.build_number = 0

        self.parse_version(version_string)

    def parse_version(self, version_string):
        if version_string is None or len(version_string) == 0:
            return

        text = version_string.split(' ')
        version_part = text[0]

        version_info = version_part.split('.')
        if len(version_info) > 0:
            self.major = int(version_info[0])

        if len(version_info) > 1:
            self.minor = int(version_info[1])

        if len(version_info) > 2:
            self.revision = int(version_info[2])

        if len(version_info) > 3:
            self.build_number = int(version_info[3])

    def __eq__(self, other):
        if self.major != other.major:
            return False

        if self.minor != other.minor:
            return False

        if self.revision != other.revision:
            return False

        if self.build_number != other.build_number:
            return False

        return True

    def __lt__(self, other):
        if self.major < other.major:
            return True
        elif self.major == other.major:
            if self.minor < other.minor:
                return True
            elif self.minor == other.minor:
                if self.revision < other.revision:
                    return True
                elif self.revision == other.revision:
                    if self.build_number < other.build_number:
                        return True

    def __gt__(self, other):
        if self.major > other.major:
            return True
        elif self.major == other.major:
            if self.minor > other.minor:
                return True
            elif self.minor == other.minor:
                if self.revision > other.revision:
                    return True
                elif self.revision == other.revision:
                    if self.build_number > other.build_number:
                        return True

        return False

    def __ge__(self, other):
        if self.__gt__(other):
            return True

        return self.__eq__(other)
