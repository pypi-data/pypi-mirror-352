import sys
import traceback
import types
import os
from .util import _log
from jennifer.agent import jennifer_agent


class MethodSelector:

    NO_PARAMETER = 0
    ALL_PARAMETER = 1
    ARG_PARAMETER_ONLY = 2
    NAMED_PARAMETER_ONLY = 4
    BOTH_PARAMETER = 6  # ARG_PARAMETER_ONLY | NAMED_PARAMETER_ONLY
    RETURN_VALUE = 8

    UNDEFINED = 0
    MODULE_FUNCTION = 1
    CLASS_STATIC_METHOD = 2
    CLASS_INSTANCE_METHOD = 4

    PROFILE_NONE = 0
    PROFILE_USER_ID = 1
    PROFILE_GUID = 2
    PROFILE_METHOD = 4

    def __init__(self, text, profile_type, profile_return_value=False):
        self.text = text
        self.profile_module = None
        self.profile_class = None
        self.profile_func_key = None
        self.profile_arg_idx = []
        self.profile_arg_names = []
        self.is_initialized = False
        self.profile_type = profile_type
        self.fqdn = None

        if profile_type == MethodSelector.PROFILE_NONE:
            return

        if profile_type == MethodSelector.PROFILE_METHOD:
            if profile_return_value:
                self.param_mode = MethodSelector.RETURN_VALUE
            else:
                self.param_mode = MethodSelector.NO_PARAMETER
        else:
            if profile_return_value:
                self.param_mode = MethodSelector.RETURN_VALUE
            else:
                self.param_mode = MethodSelector.ALL_PARAMETER

        self.original_target_container = None
        self.original_func = None
        self.func_type = MethodSelector.UNDEFINED

        try:
            self.parse_profile_item(text)
        except Exception as e:
            _log('ERROR', 'invalid profile item', text, e)
            pass

    def parse_profile_item(self, item):
        item = str(item).strip()
        items = item.split(' ')
        if len(items) < 2:
            if item.endswith('.*'):
                self.profile_module = item[0:len(item) - 2]
                self.profile_class = None
                self.fqdn = self.profile_module + ' .'
                self.profile_func_key = None
                return
            else:
                _log('[WARN]', 'invalid profile format', item)
                return
        else:
            self.profile_module = items[0].strip()

            class_or_func = items[1].strip().split('.')
            if len(class_or_func) < 2:
                if class_or_func[0].find('.') == -1:
                    self.profile_func_key = None
                    self.profile_class = class_or_func[0].strip()
                    (_, arg_info) = MethodSelector.parse_bracket(class_or_func[0].strip())
                else:
                    self.profile_func_key, arg_info = MethodSelector.parse_bracket(class_or_func[0].strip())
            else:
                self.profile_class = class_or_func[0].strip()
                if len(self.profile_class) == 0:
                    self.profile_class = None
                self.profile_func_key, arg_info = MethodSelector.parse_bracket(class_or_func[1].strip())

            if self.profile_func_key is None:
                self.fqdn = self.profile_module + ' ' + class_or_func[0] + '.'
            else:
                self.fqdn = self.profile_module + ' ' + class_or_func[0] + '.' + self.profile_func_key

        if len(items) >= 3:
            arg_text = MethodSelector.strip_curly_brace(''.join(items[2:]))
            arg_list = arg_text.split(',')
            for arg in arg_list:
                arg = arg.strip()

                try:
                    is_numeric_arg = arg.isnumeric()
                except AttributeError:
                    is_numeric_arg = unicode(arg).isnumeric()

                if arg_info is None:
                    if is_numeric_arg:
                        self.profile_arg_idx.append(int(arg))
                        self.param_mode |= MethodSelector.ARG_PARAMETER_ONLY
                    else:
                        self.profile_arg_names.append(arg)
                        self.param_mode |= MethodSelector.NAMED_PARAMETER_ONLY
                else:
                    if is_numeric_arg:
                        arg_pos = int(arg) - 1
                        if arg_pos >= len(arg_info):
                            arg_pos = arg
                        else:
                            arg_pos = arg_info[arg_pos]

                        if arg_pos.isnumeric():
                            self.profile_arg_idx.append(int(arg))
                            self.param_mode |= MethodSelector.ARG_PARAMETER_ONLY
                        else:
                            self.profile_arg_names.append(arg_pos)
                            self.param_mode |= MethodSelector.NAMED_PARAMETER_ONLY
                    else:
                        self.profile_arg_names.append(arg)
                        self.param_mode |= MethodSelector.NAMED_PARAMETER_ONLY

        self.is_initialized = True

    def __str__(self):
        return self.fqdn

    @staticmethod
    def get_profile_type_name(type_id):
        if type_id == MethodSelector.PROFILE_USER_ID:
            return "user_id"
        elif type_id == MethodSelector.PROFILE_GUID:
            return "guid"
        elif type_id == MethodSelector.PROFILE_METHOD:
            return "method"
        return "(none)"

    @staticmethod
    def parse_bracket(text):
        spos = text.find('(')
        if spos == -1:
            return text, None

        function_name = text[0:spos]
        epos = text.find(')Any')
        if epos == -1:
            return function_name, None

        arg_text = text[spos + 1:epos]
        if len(arg_text) == 0:
            return function_name, []

        arg_info = arg_text.split(',')
        return function_name, arg_info

    @staticmethod
    def strip_curly_brace(text):
        return text.strip().strip('{').strip('}')

    def gather_hook_info(self, target_hooking_func_dict):
        import importlib

        try:
            module = importlib.import_module(self.profile_module)
        except Exception as e:
            _log('INFO', 'process_dynamic_hook', 'not loaded', self.text)
            return

        container_dict = None
        class_type = None

        if self.profile_class is not None:
            class_type = module.__dict__.get(self.profile_class, None)
            if class_type is not None:
                container_dict = class_type.__dict__

        else:
            container_dict = module.__dict__

        user_func_list = []

        for item in container_dict.values():
            # 모듈인 경우 전역 함수 목록, 클래스인 경우 staticmethod와 멤버 함수 목록을 구성
            if isinstance(item, types.FunctionType) is False and isinstance(item, staticmethod) is False:
                continue

            if hasattr(item, '__name__') and item.__name__.startswith('__') is False:
                user_func_list.append(item)
            elif hasattr(item, '__func__'):
                user_func_list.append(item)

        hooked_list = []
        user_func_name = []

        for user_func in user_func_list:
            is_instance = False
            all_module_function = self.text.endswith('.*')
            func_name = None

            if class_type is not None:
                is_instance = isinstance(user_func, types.FunctionType)

                if is_instance is False:
                    if isinstance(user_func, staticmethod) is False:
                        continue  # user_func이 static/instance 멤버가 아니라면 대상에서 제외
                    else:
                        func_name = user_func.__func__.__name__
                else:
                    func_name = user_func.__name__
            else:
                func_name = user_func.__name__

            if all_module_function:
                if self.profile_module != user_func.__module__:  # import로 추가된 함수는 제외
                    continue

            if func_name is None:
                continue

            user_func_name.append(func_name)

            if self.profile_func_key is not None and func_name != self.profile_func_key:
                continue

            if self.profile_func_key is None:
                fqdn_text = self.fqdn + func_name
            else:
                fqdn_text = self.fqdn

            self.register_hook_func(target_hooking_func_dict, class_type, container_dict, user_func,
                                    fqdn_text, func_name, is_instance)
            hooked_list.append(fqdn_text)

        if len(hooked_list) == 0:
            print('[class selector] NOT FOUND: ', self.profile_func_key, 'from', user_func_name)

    def merge_param_info(self, cur_info):
        if self.param_mode == MethodSelector.RETURN_VALUE:
            cur_info[self.profile_type]['param_mode'] |= self.param_mode
            return

        if self.param_mode == MethodSelector.NO_PARAMETER:
            return

        if self.param_mode & MethodSelector.BOTH_PARAMETER:
            cur_info[self.profile_type] = {
                'item_text': self.text,
                'param_mode': self.param_mode,
                'arg_idx': self.profile_arg_idx,
                'arg_names': self.profile_arg_names,
            }

        cur_info[self.profile_type]['param_mode'] = self.param_mode

        if self.param_mode & MethodSelector.ARG_PARAMETER_ONLY:
            cur_info[self.profile_type]['arg_idx'] = self.profile_arg_idx

        if self.param_mode & MethodSelector.NAMED_PARAMETER_ONLY:
            cur_info[self.profile_type]['arg_names'] = self.profile_arg_names

    def register_hook_func(self, target_hooking_func_dict, class_type, container_dict, target_func,
                           fqdn, func_name, is_instance):
        item_key = str(target_func)

        if item_key in target_hooking_func_dict.keys():
            cur_value = target_hooking_func_dict[item_key]
            cur_value['profile_type'] = cur_value['profile_type'] | self.profile_type

            if self.profile_type in cur_value.keys():
                self.merge_param_info(cur_value)
            else:
                cur_value[self.profile_type] = {
                    'item_text': self.text,
                    'param_mode': self.param_mode,
                    'arg_idx': self.profile_arg_idx,
                    'arg_names': self.profile_arg_names,
                }
        else:
            new_value = {
                'profile_type': self.profile_type,
                'profile_func_key': func_name,
                'class_type': class_type,
                'is_instance': is_instance,
                'container_dict': container_dict,
                'target_func': target_func,
                'fqdn': fqdn,
                self.profile_type: {
                    'item_text': self.text,
                    'param_mode': self.param_mode,
                    'arg_idx': self.profile_arg_idx,
                    'arg_names': self.profile_arg_names,
                },
            }
            target_hooking_func_dict[item_key] = new_value


def append_tuple_to_list(list_inst, tuple_inst, idx=None):
    if idx is None:
        list_inst.extend([str(item) for item in tuple_inst])
    else:
        for order, item in enumerate(tuple_inst):
            if (order + 1) in idx:
                list_inst.append(str(item))


def append_dict_to_list(list_inst, dict_inst, names=None):
    if names is None:
        list_inst.extend([str(value) for key, value in dict_inst.items()])
    else:
        for key, value in dict_inst.items():
            if key in names:
                list_inst.append(str(value))


def get_value_list(param_mode, args, kwargs, arg_idx, arg_names):
    value_list = []

    if param_mode & MethodSelector.ALL_PARAMETER:
        append_tuple_to_list(value_list, args)
        append_dict_to_list(value_list, kwargs)
    else:
        if param_mode & MethodSelector.ARG_PARAMETER_ONLY:
            append_tuple_to_list(value_list, args, idx=arg_idx)

        if param_mode & MethodSelector.NAMED_PARAMETER_ONLY:
            append_dict_to_list(value_list, kwargs, names=arg_names)

    return value_list


def wrap_non_instance_method(org_func, target_hook_info):

    def inner_handler(*args, **kwargs):
        return_ctx = None
        param_mode = None
        result = None

        agent = jennifer_agent()
        max_arg_length = agent.app_config.profile_method_parameter_value_length
        max_ret_length = agent.app_config.profile_method_return_value_length

        if agent is None:
            return org_func(*args, **kwargs)

        o = agent.current_active_object()
        if o is None:
            return org_func(*args, **kwargs)

        try:
            return_ctx, param_mode = process_dynamic_pre_method_func(args, kwargs, target_hook_info, o, max_arg_length)
        except:
            pass

        error_ctx = None
        try:
            result = org_func(*args, **kwargs)
        except Exception as e:
            error_ctx = e

        try:
            if return_ctx is not None:
                process_dynamic_post_method_func(return_ctx, param_mode, error_ctx, target_hook_info, result, o,
                                                 max_ret_length)
        except:
            pass

        if error_ctx is not None:
            raise error_ctx

        return result

    return inner_handler


def wrap_class_instance_method(org_func, target_hook_info):

    def inner_handler(self, *args, **kwargs):
        return_ctx = None
        param_mode = None
        result = None

        agent = jennifer_agent()
        if agent is None:
            return org_func(self, *args, **kwargs)

        o = agent.current_active_object()
        max_arg_length = agent.app_config.profile_method_parameter_value_length
        max_ret_length = agent.app_config.profile_method_return_value_length

        if o is None:
            return org_func(self, *args, **kwargs)

        try:
            return_ctx, param_mode = process_dynamic_pre_method_func(args, kwargs, target_hook_info, o, max_arg_length)
        except:
            pass

        error_ctx = None
        try:
            result = org_func(self, *args, **kwargs)
        except Exception as e:
            error_ctx = e

        try:
            if return_ctx is not None:
                process_dynamic_post_method_func(return_ctx, param_mode, error_ctx, target_hook_info, result, o,
                                                 max_ret_length)
        except:
            pass

        if error_ctx is not None:
            raise error_ctx

        return result

    return inner_handler


def process_profile_user_id_pre_method_func(args, kwargs, param_mode, arg_idx, arg_names, o):
    if param_mode == MethodSelector.RETURN_VALUE:
        pass
    else:
        user_id_list = get_value_list(param_mode, args, kwargs, arg_idx, arg_names)
        o.set_user_id(''.join(user_id_list))


def process_profile_guid_pre_method_func(args, kwargs, param_mode, arg_idx, arg_names, o):
    if param_mode == MethodSelector.RETURN_VALUE:
        pass
    else:
        user_id_list = get_value_list(param_mode, args, kwargs, arg_idx, arg_names)
        o.set_guid(''.join(user_id_list))


def process_profile_method_pre_method_func(args, kwargs, param_mode, arg_idx, arg_names, o, fqdn, max_arg_length):
    pi_method = o.profiler.start_method(fqdn)

    if param_mode == MethodSelector.RETURN_VALUE:
        pass
    else:
        method_param_list = get_value_list(param_mode, args, kwargs, arg_idx, arg_names)
        if pi_method is not None and len(method_param_list) > 0:
            param_text = '(' + get_text_max_length(max_arg_length, ','.join(method_param_list)) + ')'
            o.profiler.add_method_parameter(pi_method.key, param_text)

    return pi_method


def get_text_max_length(max_length, text):
    if max_length < len(text):
        return text[0:max_length] + '...'

    return text


def hook_info_from(target_hook_info, info_id):
    item_info = target_hook_info[info_id]
    return item_info['param_mode'], item_info['arg_idx'], item_info['arg_names']


def process_dynamic_pre_method_func(args, kwargs, target_hook_info, o, max_arg_length):
    profile_type = target_hook_info['profile_type']

    if o is None:
        return

    return_context = None

    if profile_type & MethodSelector.PROFILE_USER_ID:
        (param_mode, arg_idx, arg_names) = hook_info_from(target_hook_info, MethodSelector.PROFILE_USER_ID)
        process_profile_user_id_pre_method_func(args, kwargs, param_mode, arg_idx, arg_names, o)

    if profile_type & MethodSelector.PROFILE_GUID:
        (param_mode, arg_idx, arg_names) = hook_info_from(target_hook_info, MethodSelector.PROFILE_GUID)
        process_profile_guid_pre_method_func(args, kwargs, param_mode, arg_idx, arg_names, o)

    if profile_type & MethodSelector.PROFILE_METHOD:
        fqdn_text = target_hook_info['fqdn']
        (param_mode, arg_idx, arg_names) = hook_info_from(target_hook_info, MethodSelector.PROFILE_METHOD)

        return_context = process_profile_method_pre_method_func(args, kwargs, param_mode, arg_idx, arg_names, o,
                                                                fqdn_text, max_arg_length)

    return return_context, param_mode


def process_dynamic_post_method_func(return_ctx, param_mode, error_ctx, target_hook_info, return_value, o,
                                     max_ret_length):
    profile_type = target_hook_info['profile_type']

    if o is None:
        return

    if profile_type & MethodSelector.PROFILE_USER_ID and param_mode & MethodSelector.RETURN_VALUE:
        o.set_user_id(str(return_value))

    if profile_type & MethodSelector.PROFILE_GUID and param_mode & MethodSelector.RETURN_VALUE:
        o.set_guid(str(return_value))

    if profile_type & MethodSelector.PROFILE_METHOD and return_ctx is not None:
        pi_method = return_ctx

        if param_mode & MethodSelector.RETURN_VALUE:
            if return_value is None:
                ret_text = 'None'
            else:
                ret_text = get_text_max_length(max_ret_length, str(return_value))
            o.profiler.add_method_return(pi_method.key, ret_text)

        o.profiler.end_method(pi_method, error_ctx)


class ClassSelector:

    def __init__(self, text_list, profile_type, profile_return_value=False):
        self.method_list = []
        self.profile_type = profile_type

        if text_list is None or len(text_list) == 0:
            return

        if isinstance(text_list, list) is False:
            return

        for text in text_list:
            parsed_item = MethodSelector(text, profile_type, profile_return_value)
            if parsed_item is None:
                continue
            self.method_list.append(parsed_item)

    def __len__(self):
        return len(self.method_list)

    def __str__(self):
        return (MethodSelector.get_profile_type_name(self.profile_type) +
                ", [" + ', '.join(str(item) for item in self.method_list) + "]")

    def preprocess_hook(self, target_hooking_func_dict):
        for method in self.method_list:
            try:
                method.gather_hook_info(target_hooking_func_dict)
            except Exception as e:
                _log('ERROR', 'preprocess_hook', method.text, e)

    @staticmethod
    def unhook_func(target_hook_info):
        try:
            original_func = target_hook_info['original_func']
            if original_func is None:
                return

            original_target_container = target_hook_info['original_target_container']
            if original_target_container is None:
                return

            func_type = target_hook_info['func_type']
            profile_func_key = target_hook_info['profile_func_key']

            if func_type == MethodSelector.MODULE_FUNCTION:
                original_target_container[profile_func_key] = original_func
            elif func_type == MethodSelector.CLASS_STATIC_METHOD:
                setattr(original_target_container, profile_func_key, staticmethod(original_func))
            elif func_type == MethodSelector.CLASS_INSTANCE_METHOD:
                setattr(original_target_container, profile_func_key, original_func)
        except Exception as e:
            _log('ERROR', 'unhook_func', original_func, e)

    @staticmethod
    def hook_func(target_func_name, target_hook_info):
        try:
            container_dict = target_hook_info['container_dict']
            target_func = target_hook_info['target_func']
            target_func_text = target_func_name
            profile_func_key = target_hook_info['profile_func_key']
            is_instance = target_hook_info['is_instance']
            class_type = target_hook_info['class_type']

            func_type = None

            if is_instance:
                func_type = MethodSelector.CLASS_INSTANCE_METHOD
                if target_func_text.find('wrap_class_instance_method.<locals>.handler') != -1:
                    return False

                setattr(class_type, profile_func_key, wrap_class_instance_method(target_func, target_hook_info))

                target_hook_info['original_target_container'] = class_type
                target_hook_info['original_func'] = target_func

                _log('INFO', 'hook_func.instance_method', target_func_text)
            else:
                if isinstance(target_func, staticmethod):
                    func_type = MethodSelector.CLASS_STATIC_METHOD
                    if target_func_text.find('wrap_class_static_method.<locals>.handler') != -1:
                        return False

                    setattr(class_type, profile_func_key,
                            staticmethod(wrap_non_instance_method(target_func.__func__, target_hook_info)))

                    target_hook_info['original_target_container'] = class_type
                    target_hook_info['original_func'] = target_func.__func__

                    _log('INFO', 'hook_func.static_method', target_func_text, target_func.__func__)
                else:
                    func_type = MethodSelector.MODULE_FUNCTION
                    if target_func_text.find('wrap_global_function.<locals>.handler') != -1:
                        return False

                    target_hook_info['original_target_container'] = container_dict
                    target_hook_info['original_func'] = target_func
                    container_dict[profile_func_key] = wrap_non_instance_method(target_func, target_hook_info)

                    _log('INFO', 'hook_func.module_func', target_func_text)

            target_hook_info['func_type'] = func_type
        except Exception as e:
            _log('ERROR', 'hook_func', target_func_name, e)

        return True
