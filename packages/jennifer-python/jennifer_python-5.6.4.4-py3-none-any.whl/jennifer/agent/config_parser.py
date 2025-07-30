
from .util import _log
import os


class ConfigParser(object):
    def __init__(self):
        self.sections = {}
        self.config_path = None
        self.multiple_key = {'ignore_url', 'ignore_url_prefix', 'ignore_url_postfix', 'profile_http_header',
                        'profile_http_parameter', 'url_additional_request_keys', 'service_user_param',
                        'service_user_return', 'service_guid_param', 'service_guid_return',
                        'profile_method_class', 'profile_method_param', 'profile_method_return',
                        'profile_method_pattern', 'skip_module', 'applist_webapp'}


    def read(self, config_path):
        self.config_path = config_path
        text = ""

        with open(config_path, 'r') as config_file:
            text = str(config_file.read()).strip()

        self._config_read_from(text)

        text = self._read_from_environment()
        self._config_read_from(text)

    def _read_from_environment(self):
        text = "[JENNIFER]" + os.linesep
        env_prefix = "aries_"
        for key, value in os.environ.items():
            key = key.strip().lower()
            if key.startswith("aries_") is False:
                continue

            key = key[len(env_prefix):]
            if key in self.multiple_key:
                value = value.strip()
                for item_value in value.split(':'):
                    item_value = item_value.strip()
                    text = text + key + "=" + item_value + os.linesep
            else:
                text = text + key + "=" + value + os.linesep

        return text

    def _config_read_from(self, text):
        current_section = ''

        for line in text.splitlines():
            line = remove_comment(line)

            section_name, is_section = ConfigParser.get_section(line, current_section)
            if is_section:
                current_section = section_name

            if current_section == '':
                continue

            if current_section not in self.sections:
                self.sections[current_section] = {}

            items = line.split('=')
            if len(items) != 2:
                continue

            key = items[0].strip(' ')
            value = items[1].strip(' ')

            key_value = self.make_key_value(current_section, key, value)

            section_dict = self.sections[current_section]
            section_dict[key] = key_value

        return None

    def has_option(self, section_name, attr_name):
        section = self.sections.get(section_name)
        if section is None:
            return False

        item = section.get(attr_name)
        if item is None:
            return False

        return True

    @staticmethod
    def get_section(line, default_section):
        if len(line) < 3:
            return default_section, False

        if line[0] != '[':
            return default_section, False

        if line[len(line) - 1] != ']':
            return default_section, False

        return line[1:len(line) - 1], True

    def make_key_value(self, section_name, key, value):
        section = self.sections.get(section_name)
        if section is None:
            return value

        old_value = None

        set_key = {'ignore_url'}

        try:
            if key in self.multiple_key:
                old_value = section.get(key)
                if old_value is None:
                    if key in set_key:
                        old_value = {value}
                    else:
                        old_value = [value]
                else:
                    if isinstance(old_value, str):
                        old_value = [old_value, value]
                    elif isinstance(old_value, list):
                        old_value.append(value)
                    elif isinstance(old_value, set):
                        old_value.add(value)
                    else:
                        _log('ERROR', 'value type not supported', old_value, type(old_value))
                        old_value = None

                return old_value
        except Exception as e:
            _log('ERROR', 'make_key_value', section_name, key, value, old_value, e)
            raise

        return value

    def get(self, section_name, key_name, default_value):
        section = self.sections.get(section_name)
        if section is None:
            return default_value

        key_value = section.get(key_name)
        if key_value is None:
            return default_value

        return key_value


def remove_after(line, cut):
    return line.split(cut)[0].strip(' ').strip()


def remove_comment(line):
    text = remove_after(line, '#')
    return remove_after(text, ';')
