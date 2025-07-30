# -*- coding: utf8 -*-
import gc
import resource
import threading
import logging
import json
import os
import platform
import sys
import zlib
import traceback
from jennifer.recorder import Recorder
from jennifer.api import task
import socket
import struct
import time
from random import random
from .active_object import ActiveObject
import subprocess
import ctypes
from jennifer.agent.int_bound_set import IntBoundSet
from jennifer.agent.python_def_visitor import PythonDefVisitor
from ..pconstants import *
from .class_info import ClassInfo
from .util import _log, _log_tb

_debug_mode = os.getenv('JENNIFER_PY_DBG')

record_types = {
    'method': 1,
    'sql': 2,
    'event_detail_msg': 3,  # errors
    'service': 4,  # app
    'txcall': 5,
    'browser_info': 6,
    'thread_stack': 8,
    'user_id': 9,
    'dbc': 10,
    'stack_trace': 11,
}


class Agent(object):
    def __init__(self, get_ctx_id_func, is_async):
        self.active_object_meter = {}
        self.active_object_meter_lock = threading.Lock()
        self.inst_id = -1
        self.domain_id = -1
        self.agent_id = 0
        self.recorder = None
        self.master_lock = threading.Lock()
        self.logger = logging.getLogger('jennifer')
        self.config_pid = 0
        self.address = ''
        self.masterConnection = None
        self.get_ctx_id_func = get_ctx_id_func
        self.app_config = None
        self.is_async = is_async
        self.python_visitor = PythonDefVisitor()

        self.apc_queue_lock = threading.Lock()
        self.apc_queue = []

        # uwsgi 호스팅인 경우 --enable-threads 옵션이 지정되지 않은 상황이라면,
        # run_timer 등의 스레드 관련 기능이 동작하지 않으므로 사후 처리를 해야 함. (TODO: 아직 미구현)
        self.thread_enabled = False
        self.text_cache_record_types = None

    def _get_max_text_length(self, text_kind):
        if self.app_config is None:
            return 0

        return self.app_config.get_attr_by_name(text_kind)

    def _init_text_cache(self):
        self.text_cache_record_types = {
            'method': IntBoundSet(length=self._get_max_text_length('max_number_of_method')),
            'sql': IntBoundSet(length=self._get_max_text_length('max_number_of_sql')),
            'event_detail_msg': IntBoundSet(length=self._get_max_text_length('max_number_of_text')),
            'service': IntBoundSet(length=self._get_max_text_length('max_number_of_text')),
            'txcall': IntBoundSet(length=self._get_max_text_length('max_number_of_text')),
            'browser_info': IntBoundSet(length=self._get_max_text_length('max_number_of_text')),
            'thread_stack': IntBoundSet(length=self._get_max_text_length('max_number_of_stack')),
            'user_id': IntBoundSet(length=self._get_max_text_length('max_number_of_stack')),
            'dbc': IntBoundSet(length=self._get_max_text_length('max_number_of_stack')),
            'stack_trace': IntBoundSet(length=self._get_max_text_length('max_number_of_stack')),
        }

    def set_context_id_func(self, func):
        self.get_ctx_id_func = func

    @staticmethod
    def gen_new_txid():
        return ctypes.c_int64(int(str(int(random() * 10000000)) + str(Agent.current_time()))).value

    def current_active_object(self, ctx_id=None):
        if ctx_id is None:
            ctx_id = self.get_ctx_id_func()

        with self.active_object_meter_lock:
            return self.active_object_meter.get(ctx_id)

    def enqueue_config_changed(self, functor):
        with self.apc_queue_lock:
            self.apc_queue.append(functor)

    def consume_apc_queue(self):
        try:
            if len(self.apc_queue) == 0:
                return

            with self.apc_queue_lock:
                for functor in self.apc_queue:
                    functor()

                self.apc_queue = []

            self.send_to_master('slave_info', {'dynamic_profile_count': self.app_config.dynamic_profile_count()})
            self.log_to_file("# of dynamic profiles: " + str(self.app_config.dynamic_profile_count()))
        except Exception as e:
            _log('ERROR', 'consume_apc_queue', e)

    # config.address == /tmp/jennifer-...sock
    # config.log_dir == /tmp
    def initialize_agent(self):
        config = {
            'address': os.environ['JENNIFER_MASTER_ADDRESS'],
            'log_dir': os.environ['JENNIFER_LOG_DIR'],
            'config_path': os.environ['JENNIFER_CONFIG_FILE'],
        }
        # config.address == /tmp/jennifer-...sock
        # config.log_dir == /tmp

        from .app_config import AppConfig
        self.address = config['address']
        self.recorder = Recorder()
        self.config_pid = os.getpid()
        self.app_config = AppConfig(self, config['config_path'])

        applist_webapp = self.app_config.get_attr_by_name('applist_webapp')
        if applist_webapp is not None:
            current_directory = os.getcwd()
            if current_directory not in applist_webapp:
                _log('INFO', 'not profile this app:', current_directory)
                return False

        self._init_text_cache()

        ret = None
        with self.master_lock:
            ret = self.connect_master()

        if ret:
            task.run_timer(self.process_agent_metric, 'jennifer-handler-thread')

        return True

    def connect_master(self):
        self.masterConnection = None

        if not os.path.exists(self.address):
            return False

        _log("INFO", "proxy address: " + self.address)
        try:
            _log("INFO", "connecting to : " + self.address)
            self.masterConnection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.masterConnection.connect(self.address)
            _log("INFO", "connected")

            self.handshake_to_master()
            _log("INFO", "initiated handshake")
            task.run_task(self.master_loop, 'jennifer-master-thread')
            return True
        except Exception as e:
            self.masterConnection = None
            return False

    def handshake_to_master(self):
        try:
            import jennifer
            agent_version = jennifer.__version__
            data = '{"app_dir": "' + os.getcwd() + '", "protocol_version":2,"agent_version":"' + agent_version \
                   + '","pid":' + str(os.getpid()) + '}'

            version = data.encode('utf-8')
            self.masterConnection.send(b'\x08jennifer' + struct.pack('>L', len(version)) + version)
        except:
            _log_tb('handshake')

    @staticmethod
    def create_instance_oid(instance_id):
        if instance_id <= 0:
            return 0
        else:
            host_id = 1 << 16
            instance_id = instance_id & 0xffff
            return host_id | instance_id

    def log_to_file(self, text):
        self.send_to_master('log_local', {'message': text})

    def master_loop(self):
        param = None

        startup_info = {'python_bin_path': os.environ['JENNIFER_PYTHON_PATH']}
        self.send_to_master('startup_info', startup_info)

        import socket
        try:
            expected_error = BrokenPipeError
        except NameError:
            expected_error = socket.error

        _log('INFO', 'agent-loop started')
        while True:
            if self.masterConnection is None:
                break

            try:
                byte_cmd_len = self.masterConnection.recv(1)

                if len(byte_cmd_len) < 1:
                    break  # failed to connect master

                cmd_len = ord(byte_cmd_len)
                cmd = self.masterConnection.recv(cmd_len)
                cmd_text = cmd.decode('utf-8')
                debug_log = self.app_config.cmd_debug == cmd_text
                param_len, = struct.unpack('>L', self.masterConnection.recv(4))

                try:
                    if param_len != 0:
                        param = json.loads(self.masterConnection.recv(param_len))
                except:
                    continue

                if cmd == b'connected':
                    try:
                        import jennifer

                        self.domain_id = param.get('domain_id')
                        self.inst_id = param.get('inst_id')
                        self.agent_id = Agent.create_instance_oid(self.inst_id)

                        log_text = 'App Initialized: ' + str(self.inst_id) + ', pid == ' + str(os.getpid())
                        self.log_to_file(log_text)

                        print("---------------- [App Initialized] ----------------------")
                        print('MachineName = ', socket.gethostname())
                        print('CWD = ', os.getcwd())
                        print('Is64BitProcess = ', platform.architecture())
                        print('Python Version = ', platform.python_version(), platform.python_implementation())
                        print('Current Path = ', os.curdir)
                        print('Jennifer Python Agent Install Path = ', os.path.dirname(os.path.dirname(__file__)))
                        print('Jennifer Server Address = ', param.get('server_address'))
                        print('Jennifer Python Agent Domain ID = ', self.domain_id)
                        print('Jennifer Python Agent Inst ID = ', str(self.inst_id) + '(' + str(self.agent_id) + ')', 'Version =',
                              jennifer.__version__)
                        print('Jennifer Python Agent Pid = ', os.getpid(), ', tid', threading.get_native_id(),
                              ', thread_ident', self.get_ctx_id_func())
                        print("---------------------------------------------------------")
                    except:
                        pass
                    continue

                if cmd == b'active_detail':
                    txid = param.get('txid')
                    request_id = param.get('request_id')
                    prevent_callstack = param.get('prevent_call_stack')
                    if txid is not None and request_id is not None:
                        data = self.get_active_service_detail(txid, prevent_callstack)
                        if data is not None:
                            data['request_id'] = request_id
                            self.send_to_master('active_detail', data)
                    continue

                if cmd == b'agent_control_gc':
                    gc.collect()
                    continue

                if cmd == b'agent_control_service_dump':
                    request_id = param.get('request_id')
                    dump_file_path = param.get('dump_file_path')
                    prevent_callstack = param.get('prevent_call_stack')
                    data = {'request_id': request_id,
                            'dump_file_path': dump_file_path,
                            'process_info': self.get_process_info(),
                            'service_list': self.get_active_object_list(prevent_callstack)}
                    self.send_to_master('agent_control_service_dump', data)
                    continue

                if cmd == b'agent_info_search_child_loaded_class_nodes':
                    request_id = param.get('request_id')
                    path_value = param.get('path_value')
                    namespace_count = param.get('namespace_count')
                    only_profileable = param.get('only_profileable')
                    data = {'request_id': request_id,
                            'class_info': self.create_loaded_class_map(namespace_count, path_value, only_profileable)}

                    self.send_to_master('agent_info_search_child_loaded_class_nodes', data)
                    continue

                if cmd == b'agentcheck_env':
                    if debug_log:
                        _log('INFO', cmd_text)

                    request_id = param.get('request_id')
                    if request_id is None:
                        continue

                    gc_threshold = [0, 0, 0]
                    gc_count = [0, 0, 0]
                    gc_stats = None
                    gc_enabled = True
                    gc_debug_flags = None

                    try:
                        gc_threshold = gc.get_threshold()
                        gc_count = gc.get_count()
                        gc_enabled = gc.isenabled()
                        gc_debug_flags = gc.get_debug()
                        gc_stats = gc.get_stats()  # Python 3.4
                    except Exception as e:
                        if debug_log:
                            _log('INFO', 'agentcheck_env', 'gc', traceback.format_exc())

                    data = Agent.get_environment_variables()
                    if data is not None:
                        if debug_log:
                            _log('INFO', 'agentcheck_env', 'get_environment_variables')

                        import jennifer.hooks
                        data['jennifer.request_id'] = str(request_id)
                        data['jennifer.hooked'] = Agent.module_list_to_str(jennifer.hooks.__hooked_module__)
                        data['jennifer.gc_threshold'] = str(gc_threshold)
                        data['jennifer.gc_count'] = str(gc_count)
                        data['jennifer.gc_stats'] = str(gc_stats)
                        data['jennifer.gc_enabled'] = str(gc_enabled)
                        data['jennifer.gc_debug'] = str(gc_debug_flags)
                        data['jennifer.python_version'] = platform.python_version()
                        data['jennifer.current_pid'] = str(os.getpid())
                        data['jennifer.agent_version'] = jennifer.__version__

                        self.send_to_master('agentcheck_env', data)

                    if debug_log:
                        _log('INFO', 'send_to_master')
                    continue

                if cmd == b'agentcheck_jar':  # "분석" / "클래스 파일 위치 검색"
                    request_id = param.get('request_id')
                    class_name = param.get('class_name')
                    if request_id is None:
                        continue

                    self.python_visitor.list_defs(os.getenv('PWD'))
                    data = {'module': self.python_visitor.find_def(class_name), 'jennifer.request_id': str(request_id)}
                    self.send_to_master('agentcheck_jar', data)
                    continue

                if cmd == b'reset_text':
                    self._init_text_cache()
                    continue

                if cmd == b'reload_config':
                    self.app_config.reload()
                    continue

                if cmd == b'gc_collect':
                    gc.collect()
                    continue

                if cmd == b'upgrade_agent':
                    agent_file_path = param.get('agent_file_path')
                    python_bin_path = os.environ['JENNIFER_PYTHON_PATH']
                    print(os.getpid(), cmd, python_bin_path, '-m', 'pip', 'install', agent_file_path)
                    subprocess.check_output([python_bin_path, '-m', 'pip', 'install', agent_file_path])
                    continue

            except (expected_error, OSError):
                break
            except Exception as e:
                _log('ERROR', 'agent-loop', e)
                if _debug_mode:
                    traceback.print_exc()
                continue

    def create_loaded_class_map(self, namespace_count, package_prefix, only_profileable):
        list_class = []

        item_dict = {}

        pkg_path = os.getcwd()
        if len(package_prefix) != 0:
            pkg_path = os.path.join(pkg_path, package_prefix)

        add_module_member_list(item_dict, package_prefix)

        for idx, pkg_info in enumerate_packages(pkg_path):
            if isinstance(pkg_info, tuple):
                module_name = pkg_info[1]
            else:
                module_name = pkg_info.name

            if module_name.startswith('_'):
                continue

            if module_name.startswith('jennifer') is True:
                continue

            if len(module_name.split('.')) != 1:
                continue

            class_item = ClassInfo(module_name, LOADED_CLASS_TREE_NODE_TYPE_PACKAGE, None)
            item_dict[module_name] = class_item.to_json()

        sorted_class = sorted(item_dict.items())
        for module_item in sorted_class:
            if len(module_item) != 2:
                continue

            list_class.append(module_item[1])

        return list_class

    @staticmethod
    def module_list_to_str(module_list):
        ret = []
        for mod_name in module_list.keys():
            ret.append(mod_name)
            ret.append('[')
            version = module_list[mod_name]['version']
            ret.append(version)
            ret.append('],')

        return ''.join(ret)

    def _get_text_cache_size(self):
        size = 0
        for k, v in self.text_cache_record_types.items():
            size = size + len(v)

        return size

    @staticmethod
    def get_environment_variables():
        ret = {}
        for name, value in os.environ.items():
            ret[name] = value

        ret['jennifer.cmd'] = sys.executable
        ret['jennifer.cmd_line'] = str(sys.argv)
        return ret

    def get_process_info(self):
        ret = {'pid': os.getpid(), 'ppid': os.getppid(), 'cpu_user': self.current_cpu_time(),
               'cpu_system': self.current_cpu_time(), 'cpu_idle': self.current_cpu_time(),
               'memory_native': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'memory_heap': 0}
        return ret

    def get_active_object_list(self, prevent_callstack):
        ret = []
        cpu_time = self.current_cpu_time()
        current_time = self.current_time()

        with self.active_object_meter_lock:
            for t in self.active_object_meter.values():
                stack = 'Failed to get a callstack'
                frame = None
                if self.is_async is True:
                    stack = 'Transaction in async mode'
                elif prevent_callstack:
                    stack = "The operation of obtaining a stack trace is not allowed"
                else:
                    ctx_id = t.get_ctx_id()
                    frame = sys._current_frames().get(ctx_id)

                if frame is not None:
                    thread_ident = t.get_ctx_id()
                    stack = ''.join(traceback.format_stack(frame))

                service_tx = {
                    'txid': t.txid,
                    'thread_id': t.vthread_id,
                    'service_name': t.path_info,
                    'elapsed': current_time - t.start_time,
                    'http_query': t.query_string,
                    'sql_count': t.sql_count,
                    'sql_time': t.sql_time,
                    'tx_time': t.external_call_time,
                    'tx_count': t.external_call_count,
                    'fetch_count': t.fetch_count,
                    'elapsed_cpu': cpu_time - t.start_cpu_time,
                    'start_time': t.start_time,
                    'stack': stack,
                    'client_address': t.client_address,
                    'status': t.status
                }

            ret.append(service_tx)

        return ret

    def get_active_service_detail(self, txid, prevent_callstack):
        ret = None
        cpu_time = self.current_cpu_time()
        current_time = self.current_time()

        with self.active_object_meter_lock:
            for t in self.active_object_meter.values():
                if t.txid == txid:
                    stack = 'Failed to get a callstack'
                    frame = None
                    if self.is_async is True:
                        stack = 'Transaction in async mode'
                    elif prevent_callstack:
                        stack = "The operation of obtaining a stack trace is not allowed"
                    else:
                        ctx_id = t.get_ctx_id()
                        frame = sys._current_frames().get(ctx_id)

                    if frame is not None:
                        stack = "PID: " + str(os.getpid())
                        if t.rthread_id != 0:
                            stack += ", Thread: " + str(t.rthread_id)

                        thread_ident = t.get_ctx_id()
                        vthread_ident = thread_ident & 0xFFFFFFFF
                        stack += ", ident: " + str(thread_ident) + " (" + str(vthread_ident) + ")"
                        stack += os.linesep + ''.join(traceback.format_stack(frame))

                    ret = {
                        'guid': t.guid,
                        'txid': t.txid,
                        'thread_id': t.vthread_id,
                        'service_name': t.path_info,
                        'elapsed': current_time - t.start_time,
                        'method': t.request_method,
                        'http_query': t.query_string,
                        'sql_count': t.sql_count,
                        'sql_time': t.sql_time,
                        'tx_time': t.external_call_time,
                        'tx_count': t.external_call_count,
                        'fetch_count': t.fetch_count,
                        'cpu_time': cpu_time - t.start_cpu_time,
                        'start_time': t.start_time,
                        'stack': stack,
                        'browser_info': t.browser_info,
                        'client_address': t.client_address,
                    }

                    if t.sql_call is not None:
                        ret['sql_hash'] = t.sql_hash
                        ret['sql_cur_time'] = current_time - t.start_time - t.sql_start_time

                    break

        if ret is None:
            ret = {
                'txid': 0,
            }

        return ret

    def process_agent_metric(self):
        try:
            metrics = self.recorder.record_self()
            self.send_to_master('record_metric', metrics)

            current_cpu = Agent.current_cpu_time()
            current_time = Agent.current_time()

            copied_dict = None
            with self.active_object_meter_lock:
                copied_dict = self.active_object_meter.copy()

            ax_list = [t.to_active_service_dict(current_time, current_cpu) for t in
                       copied_dict.values()]

            self.send_to_master('active_service_list', {
                'active_services': ax_list,
            })
        except Exception as e:
            _log('ERROR', 'process_agent_metric', e)

    def send_to_master(self, cmd, params):
        try:
            p = json.dumps(params, default=str).encode('utf-8')

            pack = struct.pack('>B', len(cmd)) + cmd.encode('utf-8') + struct.pack('>L', len(p)) + p
            with self.master_lock:
                if self.masterConnection is None:
                    if not self.connect_master():
                        return False
                self.masterConnection.send(pack)
                return True

        except socket.error as e:  # except (BrokenPipeError, OSError):  # 3.x only

            import errno
            if e.errno != errno.EPIPE:  # 2.7 backward compatibility
                _log('ERROR', 'send_to_master', e)
            self.masterConnection = None

        return False

    @staticmethod
    def current_time():
        """
        current time as milli-seconds (int)
        """
        return int(time.time() * 1000)

    @staticmethod
    def current_cpu_time():
        """
        process time as milli-seconds (int)
        python [~3.3): time.clock
        python [3.3 ~]: time.process_time
        """
        if hasattr(time, 'process_time'):
            return int(time.process_time() * 1000)
        return int(time.clock() * 1000)

    def start_trace(self, environ, wmonid, path_info):
        txid = Agent.gen_new_txid()
        ctx_id = self.get_ctx_id_func()
        active_object = ActiveObject(
            agent=self,
            txid=txid,
            environ=environ,
            wmonid=wmonid,
            ctx_id=ctx_id,
            path_info=path_info,
        )

        with self.active_object_meter_lock:
            self.active_object_meter[ctx_id] = active_object

        self.send_to_master('start_service', {})
        return active_object

    def send_profile(self, profiler, profile_data):
        json_data = profiler.to_json_packet(profile_data)
        self.send_to_master('mid_profile', {
            'profile_data': json_data,
        })

    def end_trace(self, o):
        try:
            with self.active_object_meter_lock:
                self.active_object_meter.pop(o.ctx_id, None)

            pi_method = o.profiler.pop_thread_profile()

            self.send_to_master('end_service', {
                'xview_data': o.to_xview_data(pi_method),
                'profile_data': o.profiler.to_json_packet(),
            })

            # uwsgi 환경의 --enable-threads 옵션이,
            #  없는 경우를 위한 처리 추가
            #  있는 경우 어차피 run_timer 내에서 처리
            if len(self.active_object_meter) == 0:
                self.process_agent_metric()

        except Exception as e:
            _log('ERROR', 'etx', e)

    @staticmethod
    def _hash_text(text):
        hash_value = zlib.crc32(text.encode('utf-8'))
        hash_value = hash_value & 0xFFFFFFFF
        hash_value = ctypes.c_int32(hash_value).value
        return hash_value

    def _text_cache_add(self, text_kind, text_hash_code):
        text_cache = self.text_cache_record_types.get(text_kind, None)
        if text_cache is None:
            return

        text_cache.append(text_hash_code)

    def _text_cache_contains(self, text_kind, text_hash_code):
        text_cache = self.text_cache_record_types.get(text_kind, None)
        if text_cache is None:
            return False

        return text_cache.contains(text_hash_code)

    def hash_text(self, text, text_kind='service'):
        if text is None or len(text) == 0:
            return 0

        text_hash_code = self._hash_text(text)
        if self._text_cache_contains(text_kind, text_hash_code) is True:
            return text_hash_code

        sent = self.send_to_master('record_text', {
            'type': record_types.get(text_kind, 0),
            'text': text,
            'text_hash': text_hash_code,
        })

        if sent is True:
            self._text_cache_add(text_kind, text_hash_code)

        return text_hash_code


def enumerate_packages(path):
    import pkgutil

    def onerror_package(name):
        pass

    return enumerate(pkgutil.walk_packages([path], onerror=onerror_package))


def add_class_method_list(item_dict, cls_full_name):
    dot_pos = cls_full_name.rfind('.')
    if dot_pos == -1:
        return

    import importlib
    import inspect

    python_module_name = cls_full_name[:dot_pos]
    class_name = cls_full_name[dot_pos + 1:]

    try:
        python_module = importlib.import_module(python_module_name)
    except:
        return

    class_instance = python_module.__dict__[class_name]
    if class_instance is None:
        return

    if inspect.isclass(class_instance) is not True:
        return

    for member_name in class_instance.__dict__:
        if member_name.startswith('_'):
            continue

        member_instance = class_instance.__dict__[member_name]

        is_function_member = inspect.isfunction(member_instance)
        is_method_member = inspect.ismethod(member_instance)
        is_static_method_member = isinstance(member_instance, staticmethod)

        if is_static_method_member is not True and is_function_member is not True and is_method_member is not True:
            continue

        try:
            func_instance = member_instance
            if is_static_method_member:
                func_instance = member_instance.__func__

            if hasattr(inspect, 'signature'):  # python 3.3 or later
                method_sig = inspect.signature(func_instance)
                member_name += get_method_signature(method_sig)
            else:
                arg_specs = inspect.getargspec(func_instance)
                member_name += get_method_arg_spec(arg_specs)
        except Exception as e:
            continue

        full_name = cls_full_name + '.' + member_name
        member_item = ClassInfo(member_name, LOADED_CLASS_TREE_NODE_TYPE_METHOD, None)
        item_dict[full_name] = member_item.to_json()


def get_method_signature(arg_specs):
    import inspect

    method_signature_list = []
    positional_arg = 1
    for param_item in arg_specs.parameters.values():
        parameter_name = param_item.name
        if parameter_name == 'self':
            continue

        if param_item.default == inspect.Parameter.empty:
            method_signature_list.append(str(positional_arg))
            positional_arg += 1
        else:
            method_signature_list.append(parameter_name)

    return '(' + ','.join(method_signature_list) + ')Any'


def get_method_arg_spec(arg_specs):
    arg_list = arg_specs[0]
    default_cnt = 0
    if arg_specs[3] is not None:
        default_cnt = len(arg_specs[3])

    method_signature_list = []
    positional_arg = 1
    for idx, parameter_name in enumerate(arg_list):
        if parameter_name == 'self':
            continue

        if default_cnt > 0 and idx >= len(arg_list) - default_cnt:
            method_signature_list.append(parameter_name)
        else:
            method_signature_list.append(str(positional_arg))
        positional_arg += 1

    return '(' + ','.join(method_signature_list) + ')Any'


def add_module_member_list(item_dict, python_module_name):
    if len(python_module_name) == 0:
        return

    import importlib
    import inspect

    try:
        python_module = importlib.import_module(python_module_name)
    except:
        add_class_method_list(item_dict, python_module_name)
        return

    if python_module is None:
        return

    for member_name in python_module.__dict__:
        member_instance = python_module.__dict__[member_name]
        if member_instance is None:
            continue

        is_class_member = inspect.isclass(member_instance)
        is_function_member = inspect.isfunction(member_instance)
        is_method_member = inspect.ismethod(member_instance)

        if is_class_member is not True and is_function_member is not True and is_method_member is not True:
            continue

        if member_name.startswith('_'):
            continue

        if is_class_member is True:
            module_name = member_instance.__module__
            if python_module_name != module_name:
                continue

        full_name = python_module_name + '.' + member_name

        if is_class_member:
            member_item = ClassInfo(member_name, LOADED_CLASS_TREE_NODE_TYPE_CLASS, None)
        else:
            if hasattr(inspect, 'signature'):  # python 3.3 or later
                method_sig = inspect.signature(member_instance)
                member_name += get_method_signature(method_sig)
            else:
                arg_specs = inspect.getargspec(member_instance)
                member_name += get_method_arg_spec(arg_specs)

            member_item = ClassInfo(member_name, LOADED_CLASS_TREE_NODE_TYPE_METHOD, None)
        item_dict[full_name] = member_item.to_json()
