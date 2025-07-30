import base64
import os
from datetime import datetime

enable_diagnostics = os.getenv('JENNIFER_DBG') == '1'
diagnostics_to_file = os.getenv('JENNIFER_LOG_FILE') or None


def truncate_value(value, max_length):
    if len(value) > max_length:
        return value[:max_length] + '...'

    return value[:max_length]


def encode_base64_cookie(data):
    return base64.b64encode(data).decode('ascii').replace('=', '%3D')


def decode_base64_cookie(data):
    return base64.b64decode(data.replace('%3D', '='))


def process_url_additional_request_keys(dict_instance, req_uri, key_list, value_length):
    text = []

    for param_key in key_list:
        param_value = dict_instance.get(param_key)
        if param_value is None:
            continue

        if isinstance(param_value, list):
            text.append(param_key + '=' + truncate_value(','.join(param_value), value_length))
        elif isinstance(param_value, str):
            text.append(param_key + '=' + truncate_value(param_value, value_length))

    if len(text) == 0:
        return req_uri

    return req_uri + '+(' + '&'.join(text) + ')'


def profile_http_parameter_message(o, dict_instance, param_list, value_length):
    text = []

    for param_key in param_list:
        param_value = dict_instance.get(param_key)
        if param_value is None:
            continue

        if isinstance(param_value, list):
            text.append(param_key + '=' + truncate_value(','.join(param_value), value_length))
        elif isinstance(param_value, str):
            text.append(param_key + '=' + truncate_value(param_value, value_length))

    if len(text) != 0:
        o.profiler.add_message('HTTP-PARAM: ' + '; '.join(text))


def is_ignore_urls(agent, req_uri):
    if agent is None:
        return True

    if agent.app_config.ignore_url_postfix is not None:
        for ext in agent.app_config.ignore_url_postfix:
            if req_uri.endswith(ext):
                return True

    if agent.app_config.ignore_url is not None:
        if req_uri in agent.app_config.ignore_url:
            return True

    if agent.app_config.ignore_url_prefix is not None:
        for ext in agent.app_config.ignore_url_prefix:
            if req_uri.startswith(ext):
                return True

    return False


def format_time(time_value):
    return time_value.strftime("[%Y-%m-%d %H:%M:%S]")


def _log(level, *args):
    time_now = datetime.now()
    time_column = format_time(time_now)

    print(time_column, '[' + str(os.getpid()) + ']', level, '[jennifer]', args)

    if enable_diagnostics is False:
        return

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