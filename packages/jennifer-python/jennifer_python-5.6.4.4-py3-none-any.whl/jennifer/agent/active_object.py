# -*- coding: utf8 -*-
from random import random
from jennifer.agent import jennifer_agent
from .profiler import PiProfiler
from jennifer.pconstants import *
from jennifer.protocol import PiSqlFetch
import platform
import ctypes
import threading
from .util import VersionInfo


class ActiveObject:
    current_python_ver = VersionInfo(platform.python_version())
    python38_version = VersionInfo("3.8.0")
    _is_38_or_later = python38_version <= current_python_ver

    def __init__(self, agent, environ, wmonid, txid, ctx_id, path_info):

        self.elapsed = 0
        self.elapsed_cpu = 0

        self.sql_hash = 0
        self.sql_count = 0
        self.sql_call = None
        self.sql_start_time = 0
        self.sql_time = 0
        self.fetch_count = 0
        self.fetch_time = 0
        self.running_profile_number_or_n1 = -1

        self.external_call = None
        self.external_call_count = 0
        self.external_call_time = 0
        self.external_call_name = None
        self.external_call_started = False
        self.external_call_type = REMOTE_CALL_TYPE_NONE

        self.txid = txid
        self.wmonid = wmonid
        self.user_hash = 0
        self.guid = None
        self.error_code = 0
        self.http_status_code = 0
        self.service_hash = 0
        self.incoming_remote_call = None
        self.running_data_source_name = None
        self.fetch_pi = None

        if ActiveObject._is_38_or_later:
            self.rthread_id = threading.get_native_id()
        else:
            self.rthread_id = 0

        self.agent = agent
        self.end_system_time = 0
        self.wmonid = wmonid

        # 비동기(async): thread_id (4바이트) == ctx_id (ContextVars에 의해 설정한 4바이트)
        # 동기(sync): thread_id (4바이트) != thread id (최소 6바이트)
        self.ctx_id = ctx_id

        # 단순히 제니퍼 서버와 통신을 위한 thread id
        self.vthread_id = ctx_id & 0xFFFFFFFF
        self.client_address = self.get_remote_address(environ)

        self.browser_info = environ.get('HTTP_USER_AGENT', '')
        self.browser_info_hash = self.agent.hash_text(self.browser_info, 'browser_info')

        self.request_method = environ.get('REQUEST_METHOD', '')
        self.query_string = environ.get('QUERY_STRING', '')

        self.start_time = agent.current_time()
        self.start_cpu_time = agent.current_cpu_time()

        self.path_info = path_info
        self.service_hash = self.agent.hash_text(path_info)

        self.status = ACTIVE_SERVICE_STATUS_CODE_INITIALIZING
        self.profiler = PiProfiler(self, self.service_hash)

        self.outgoing_key = 0
        self.outgoing_sid = 0
        self.outgoing_agent_id = 0

        self.incoming_key = 0
        self.incoming_sid = 0
        self.incoming_agent_id = 0
        self.type_on_service = 0
        self.incoming_type = INCOMING_OUTGOING_TYPE_NONE

    def set_user_id(self, user_id):
        self.user_hash = self.agent.hash_text(user_id, 'user_id')

    def set_guid(self, guid_text):
        self._make_guid_max_length(guid_text)

    def create_guid_for_sure(self):
        if self.guid is None:
            self._make_guid_max_length()
            self.profiler.add_message('GUID=[%s]' % self.guid)

    def _make_guid_max_length(self, uuid_text=None):
        if uuid_text is None:
            self.guid = '%016x' % self.txid
        else:
            self.guid = uuid_text

        max_length = self.agent.app_config.guid_max_length
        if 0 < max_length < len(self.guid):
            self.guid = self.guid[:max_length]

    def initialize(self, root_method_name):
        method_hash = self.agent.hash_text(root_method_name, 'method')
        if method_hash != 0:
            self.profiler.push_thread_profile(method_hash)

        if self.guid is None:
            if self.agent.app_config.enable_guid_from_txid:
                self._make_guid_max_length()
        else:
            self.profiler.add_message('RECV GUID=[%s]' % self.guid)

    def get_method_thread_cpu_time(self, start_cpu, pi_start_cpu=0):
        result = 0
        if start_cpu != 0:  # profile_method_cpu
            result = self.agent.current_cpu_time() - start_cpu - pi_start_cpu
            if result < 0:
                result = 0

        return result

    def get_current_point_time(self):
        result = self.agent.current_time() - self.start_time
        if result < 0:
            result = 0
        return result

    def get_end_of_cpu_time(self):
        result = self.agent.current_cpu_time() - self.start_cpu_time
        if result < 0:
            result = 0
        return result

    def set_status(self, status):
        self.status = status

    def set_fetch_status(self):
        if self.status == ACTIVE_SERVICE_STATUS_CODE_SQL_RS_OPEN:
            return self.fetch_pi
        else:
            self.status = ACTIVE_SERVICE_STATUS_CODE_SQL_RS_OPEN
            self.fetch_pi = PiSqlFetch(self)

        return self.fetch_pi

    def clear_fetch_status(self):
        self.status = ACTIVE_SERVICE_STATUS_CODE_RUN
        self.fetch_pi = None

    def get_status(self):
        return self.status

    def get_ctx_id(self):
        return self.ctx_id

    def to_active_service_dict(self, current_time, current_cpu_time):
        self.elapsed_cpu = current_cpu_time - self.start_cpu_time
        self.elapsed = current_time - self.start_time

        running_mode = ACTIVE_SERVICE_RUNNING_MODE_NONE
        running_hash = 0
        running_time = 0

        outgoing_remote_call = None
        incoming_call = self.create_incoming_remote_call_info()

        if self.sql_call is not None:
            running_mode = ACTIVE_SERVICE_RUNNING_MODE_SQL
            running_hash = self.sql_hash
            running_time = current_time - self.start_time - self.sql_start_time

            if self.sql_call.outgoing_remote_call is not None:
                outgoing_remote_call = self.sql_call.outgoing_remote_call.to_dict()

        elif self.external_call is not None:
            running_mode = ACTIVE_SERVICE_RUNNING_MODE_EXTERNALCALL
            running_hash = self.external_call.desc_hash
            running_time = current_time - self.start_time - self.external_call.start_time

            if self.external_call.outgoing_remote_call is not None:
                outgoing_remote_call = self.external_call.outgoing_remote_call.to_dict()

        data = {'service_hash': self.service_hash, 'elapsed': self.elapsed, 'txid': self.txid, 'wmonid': self.wmonid,
                'thread_id': self.vthread_id, 'client_address': self.client_address, 'elapsed_cpu': self.elapsed_cpu,
                'sql_count': self.sql_count, 'fetch_count': self.fetch_count, 'start_time': self.start_time,
                'running_mode': running_mode, 'running_hash': running_hash,
                'running_time': running_time, 'status_code': self.status,
                'outgoing_remote_call': outgoing_remote_call, 'incoming_remote_call': incoming_call}

        return data

    def create_incoming_remote_call_info(self):
        incoming_call = None
        if self.incoming_type != INCOMING_OUTGOING_TYPE_NONE:
            incoming_call = {'type': self.incoming_type, 'key': self.incoming_key, 'sid': self.incoming_sid,
                             'agent_id': self.incoming_agent_id}
        return incoming_call

    def set_incoming_info(self, call_type_id, incoming_key, incoming_sid, incoming_agent_id):
        if call_type_id is None:
            self.type_on_service = REMOTE_CALL_TYPE_HTTP

        if incoming_key is not None and incoming_sid is not None and incoming_agent_id is not None:
            self.incoming_key = ctypes.c_int64(int(incoming_key)).value
            self.incoming_sid = int(incoming_sid)
            self.incoming_agent_id = int(incoming_agent_id)
            self.incoming_type = INCOMING_OUTGOING_TYPE_INCOMING

    def to_xview_data(self, service_method):
        self.elapsed_cpu = service_method.end_cpu
        self.elapsed = service_method.elapsed_time
        end_time = service_method.end_time

        data = {'txid': self.txid, 'elapsed': self.elapsed, 'elapsed_cpu': self.elapsed_cpu, 'end_time': end_time,
                'sql_count': self.sql_count, 'sql_time': self.sql_time, 'fetch_count': self.fetch_count,
                'fetch_time': self.fetch_time, 'external_call_count': self.external_call_count,
                'external_call_time': self.external_call_time, 'client_address': self.client_address,
                'wmonid': self.wmonid, 'user_hash': self.user_hash, 'service_hash': self.service_hash,
                'guid': self.guid,
                'browser_info_hash': self.browser_info_hash, 'error_code': self.error_code,
                'incoming_type': self.incoming_type, 'incoming_key': self.incoming_key,
                'incoming_sid': self.incoming_sid, 'incoming_agent_id': self.incoming_agent_id}

        return data

    def get_remote_address(self, environ):
        remote_addr = environ.get('REMOTE_ADDR', '')

        try:
            if self.agent.app_config.remote_address_header_key is None:
                return remote_addr

            address_from_key = environ.get("HTTP_" + self.agent.app_config.remote_address_header_key, None)
            if address_from_key is None:
                return remote_addr

            if self.agent.app_config.remote_address_header_key_delimiter is not None:
                addresses = address_from_key.split(self.agent.app_config.remote_address_header_key_delimiter)
                if len(addresses) > 1:
                    address_from_key = addresses[self.agent.app_config.remote_address_header_key_idx].strip()

            remote_addr = address_from_key
        except:
            pass
        return remote_addr
