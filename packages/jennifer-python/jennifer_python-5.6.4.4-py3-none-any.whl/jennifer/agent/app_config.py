# -*- coding: utf8 -*-
import os
import traceback
import sys
import ctypes
from jennifer.agent.class_selector import ClassSelector, MethodSelector
from .util import _log


def to_boolean(value):
    return str(value).lower() == "true"


def to_int32(value):
    return ctypes.c_int(int(value)).value


_defaultValues = {
    "enable_sql_trace": True,

    "ignore_url": None,
    "ignore_url_prefix": None,
    "ignore_url_postfix": [".css", ".js", ".ico"],
    "url_additional_request_keys": None,

    "applist_webapp": None,

    "max_number_of_method": 30000,
    "max_number_of_text": 20000,
    "max_number_of_sql": 10000,
    "max_number_of_stack": 30000,
    "profile_max_size": 1000,

    "dump_http_query": True,

    "enable_http_only_for_wmonid_cookie": False,
    "enable_secure_for_wmonid_cookie": False,
    "expire_date_for_wmonid_cookie": 365,

    "min_sql_fetch_time_to_collect": 0,
    "min_sql_time_to_collect": 0,
    "min_sql_time_to_collect_parameter": 0,

    "service_dump_dir": "/tmp",

    "guid_max_length": -1,
    "enable_guid_from_txid": False,
    "guid_http_header_key": "_J_GUID_",

    "redis_as_external_call": False,
    "topology_http_header_key": "X-J_HTTP_TUID_",
    "topology_mode": True,
    "profile_http_header_all": False,

    "profile_http_header": None,
    "profile_http_value_length": 40,
    "profile_method_return_value_length": 80,
    "sql_profile_bind_param_length": 50,
    "enable_multi_tier_trace": True,

    "profile_http_parameter": None,

    "enable_parse_sql": True,
    "enable_parse_sql_table_name": True,

    "remote_address_header_key": None,
    "remote_address_header_key_delimiter": ",",
    "remote_address_header_key_idx": 0,
    "service_naming_by_http_header": None,

    "sql_fetch_warning_count": 10000,

    "kubernetes_cluster": None,
    "kubernetes_namespace": None,

    "service_user_param": None,
    "service_user_return": None,
    "service_guid_param": None,
    "service_guid_return": None,
    "profile_method_class": None,
    "profile_method_param": None,
    "profile_method_return": None,
    "profile_method_pattern": None,

    "profile_method_parameter_value_length": 80,

    "skip_module": None,
}

_valueFunc = {
    "enable_sql_trace": to_boolean,

    # ignore_url, ignore_url_prefix, ignore_url_postfix - make_key_value 함수 내에서 직접 처리
    # url_additional_request_keys - make_key_value 함수 내에서 직접 처리

    "max_number_of_method": to_int32,
    "max_number_of_text": to_int32,
    "max_number_of_sql": to_int32,
    "max_number_of_stack": to_int32,
    "profile_max_size": to_int32,

    "dump_http_query": to_boolean,

    "enable_http_only_for_wmonid_cookie": to_boolean,
    "enable_secure_for_wmonid_cookie": to_boolean,
    "expire_date_for_wmonid_cookie": to_int32,

    "min_sql_fetch_time_to_collect": to_int32,
    "min_sql_time_to_collect": to_int32,
    "min_sql_time_to_collect_parameter": to_int32,

    # service_dump_dir 문자열

    "guid_max_length": to_int32,
    "enable_guid_from_txid": to_boolean,
    # guid_http_header_key 문자열

    "redis_as_external_call": to_boolean,
    # topology_http_header_key 문자열
    "topology_mode": to_boolean,
    "profile_http_header_all": to_boolean,

    # profile_http_header - make_key_value 함수 내에서 직접 처리
    "profile_http_value_length": to_int32,
    "profile_method_return_value_length": to_int32,
    "sql_profile_bind_param_length": to_int32,
    "enable_multi_tier_trace": to_boolean,
    
    # profile_http_parameter 문자열

    "enable_parse_sql": to_boolean,
    "enable_parse_sql_table_name": to_boolean,
    
    # remote_address_header_key 문자열
    # remote_address_header_key_delimiter 문자열
    "remote_address_header_key_idx": to_int32,
    # service_naming_by_http_header 문자열

    "sql_fetch_warning_count": to_int32,

    # kubernetes_cluster 문자열
    # kubernetes_namespace 문자열

    # service_user_param - make_key_value 함수 내에서 직접 처리
    # service_user_return - make_key_value 함수 내에서 직접 처리
    # service_guid_param - make_key_value 함수 내에서 직접 처리
    # service_guid_return - make_key_value 함수 내에서 직접 처리
    # profile_method_class - make_key_value 함수 내에서 직접 처리
    # profile_method_param - make_key_value 함수 내에서 직접 처리
    # profile_method_return - make_key_value 함수 내에서 직접 처리
    # profile_method_pattern - make_key_value 함수 내에서 직접 처리
    # applist_webapp - make_key_value 함수 내에서 직접 처리

    "profile_method_parameter_value_length": to_int32,

    # skip_module - make_key_value 함수 내에서 직접 처리
}


class AppConfig(object):
    def __init__(self, agent_instance, config_path):
        self.path = None
        self.config = None

        self.service_user_param_selector = None
        self.service_user_return_selector = None
        self.service_guid_param_selector = None
        self.service_guid_return_selector = None
        self.profile_method_class_selector = None
        self.profile_method_param_selector = None
        self.profile_method_return_selector = None
        self.profile_method_pattern_selector = None

        self.applist_webapp = None

        self.selector_list = []
        self.cache = {}
        self.agent = agent_instance
        self.target_hooking_func_dict = {}

        self._load_config(config_path)

    def get_attr_by_name(self, attr_name):
        return self.__getattr__(attr_name)

    def __getattr__(self, attr_name):
        cached_value = self.cache.get(attr_name)
        if cached_value is not None:
            return cached_value

        if self.config is None:
            return None

        try:
            value_func = _valueFunc.get(attr_name)
            default_value = _defaultValues.get(attr_name)

            if not self.config.has_option('JENNIFER', attr_name):
                attr_value = self.config.get('SERVER', attr_name, default_value)
            else:
                attr_value = self.config.get('JENNIFER', attr_name, default_value)

            if attr_value is None:
                return None

            if value_func is None:
                self.cache[attr_name] = attr_value
                return attr_value

            result = value_func(attr_value)
            self.cache[attr_name] = result

            return result
        except:
            return None

    def reload(self):
        self._load_config(self.path)

    def _load_adapter(self):
        pass

    def dynamic_profile_count(self):
        return len(self.target_hooking_func_dict)

    def _unload_dynamic_profile(self):
        for _, value in self.target_hooking_func_dict.items():
            ClassSelector.unhook_func(value)

    def _load_dynamic_profile(self):
        try:
            self._unload_dynamic_profile()

            self.service_user_param_selector = ClassSelector(self.service_user_param, MethodSelector.PROFILE_USER_ID)
            self.service_user_return_selector =\
                ClassSelector(self.service_user_return, MethodSelector.PROFILE_USER_ID, profile_return_value=True)

            self.service_guid_param_selector = ClassSelector(self.service_guid_param, MethodSelector.PROFILE_GUID)
            self.service_guid_return_selector =\
                ClassSelector(self.service_guid_return, MethodSelector.PROFILE_GUID, profile_return_value=True)

            self.profile_method_class_selector = ClassSelector(self.profile_method_class, MethodSelector.PROFILE_METHOD)
            self.profile_method_param_selector = ClassSelector(self.profile_method_param, MethodSelector.PROFILE_METHOD)
            self.profile_method_return_selector =\
                ClassSelector(self.profile_method_return, MethodSelector.PROFILE_METHOD, profile_return_value=True)

            self.profile_method_pattern_selector = ClassSelector(self.profile_method_pattern,
                                                                 MethodSelector.PROFILE_METHOD)

            self.selector_list = [
                self.service_user_param_selector,
                self.service_user_return_selector,
                self.service_guid_param_selector,
                self.service_guid_return_selector,

                self.profile_method_class_selector,
                self.profile_method_param_selector,
                self.profile_method_return_selector,

                self.profile_method_pattern_selector
            ]

            self._process_dynamic_hook()

            self.log_profiled()

        except Exception as e:
            _log('ERROR', 'load_dynamic_profile', e)

    def log_profiled(self):
        try:
            for selector in self.selector_list:
                if len(selector) != 0:
                    self.agent.log_to_file('[user-profile] ' + str(selector))

            for (key, hooked) in self.target_hooking_func_dict.items():
                hooked_func_key = hooked['profile_func_key']
                target_dict = hooked['container_dict']

                hooked_func = target_dict[hooked_func_key]

                self.agent.log_to_file('[profiled] ' + hooked['fqdn'] + ' -> ' + str(hooked_func))
        except Exception as e:
            _log('[WARN]', 'log_profiled', e)

    def _process_dynamic_hook(self):
        target_hooking_func_dict = {}
        for selector in self.selector_list:
            if selector is not None:
                selector.preprocess_hook(target_hooking_func_dict)

        for key, value in target_hooking_func_dict.items():
            ClassSelector.hook_func(key, value)

        self.target_hooking_func_dict = target_hooking_func_dict

    def _load_config(self, config_path):
        from jennifer.agent import config_parser

        if config_path is None:
            return

        print_out = sys.stdout
        if sys.stdout.closed:
            print_out = sys.stderr

        try:
            self.path = config_path
            self.config = config_parser.ConfigParser()

            if len(self.cache) != 0:
                msg = str(os.getpid()) + ' jennifer ' + 'config_changed' + os.linesep
                print_out.write(msg)

            self.cache = {}
            self.config.read(config_path)

            self._load_adapter()

            self.agent.enqueue_config_changed(lambda: self._load_dynamic_profile())
        except Exception as e:
            msg = str(os.getpid()) + ' jennifer.exception ' + 'load_config ' + config_path + ' ' + str(e) + os.linesep
            print_out.write(msg)
            traceback.print_exc()
