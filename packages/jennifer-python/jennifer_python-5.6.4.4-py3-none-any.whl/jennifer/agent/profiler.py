import datetime
from jennifer.protocol import PiFile, PiSocket, PiMessage, PiMethod, PiError, PiExternalCall, \
    PiDBMessage, PiSql, PiSqlFetch, PiMethodParameter, PiMethodReturn
from jennifer.recorder.db import DBConnectionRecorder
from jennifer.protocol.remote_call import *


class PiProfiler:
    profile_buffer_size = 512

    def __init__(self, active_object, service_hash):
        self.agent = active_object.agent
        self.active_object = active_object
        self.db_recorder = DBConnectionRecorder()

        self.profile_current_size = 0

        self.profile_max_size = 1000
        self.profile_this_idx = 0
        self.profile_parent_idx = -1
        self._profile_pos = 0
        self._profile_entry = [None] * self.profile_max_size
        self.thread_profile_item = None

    def push_thread_profile(self, hash_code):
        pi_method = PiMethod(self.active_object, hash_code)
        self.push_profile(pi_method)
        self.thread_profile_item = pi_method

    def pop_thread_profile(self):
        if self.thread_profile_item is None:
            return None

        o = self.active_object
        pi = self.thread_profile_item
        pi.end_cpu = o.get_end_of_cpu_time()
        pi.end_time = self.agent.current_time()
        pi.elapsed_time = pi.end_time - o.start_time

        if pi.end_time < pi.end_cpu:
            diff = pi.end_cpu - pi.end_time
            pi.end_time += diff
            pi.elapsed_time += diff

        self.pop_profile(pi)
        self.thread_profile_item = None

        return pi

    def add_message(self, text):
        o = self.active_object
        pi_msg = PiMessage(o, text)
        pi_msg.start_cpu = o.get_method_thread_cpu_time(o.start_cpu_time)
        self.add_profile(pi_msg)

    def add_method_parameter(self, method_key, value):
        o = self.active_object
        pi_method_parameter = PiMethodParameter(o, method_key, value)
        self.add_profile(pi_method_parameter)

    def add_method_return(self, method_key, value):
        o = self.active_object
        pi_method_return = PiMethodReturn(o, method_key, value)
        self.add_profile(pi_method_return)

    def start_method(self, text):
        o = self.active_object

        hash_code = self.agent.hash_text(text, 'method')
        pi = PiMethod(o, hash_code)

        if self.push_limited_profile(pi) is False:
            return None

        return pi

    def end_method(self, pi, exception):
        if pi is None:
            return

        o = self.active_object
        pi.end_time = o.get_current_point_time() - pi.start_time
        pi.elapsed_time = pi.end_time
        pi.end_cpu = o.get_method_thread_cpu_time(o.start_cpu_time, pi.start_cpu)

        if exception is not None:
            self.profile_exception_event(ERROR_TYPE_METHOD_EXCEPTION, str(exception))

        self.pop_profile(pi)

    def profile_exception_event(self, error_type, error_message, as_exception=False):
        o = self.active_object

        if as_exception is True:
            o.error_code = error_type
            hash_code = self.agent.hash_text(error_message, 'event_detail_msg')
            pi_error = PiError(o, error_type, hash_code)
            self.add_profile(pi_error)
        else:
            self.add_null_profile(o, error_message)

    def profile_warning_event(self, warning_type):
        o = self.active_object

        if o.error_code == 0:
            o.error_code = warning_type

        o.agent.send_to_master('record_warning', {
            'warning_type': warning_type,
            'txid': o.txid,
            'oid': o.agent.agent_id,
        })

    def add_null_profile(self, o, error_message):
        if o is None:
            return

        pi = PiMessage(o, error_message)
        self.add_profile(pi)

    def add_service_error_profile(self, exception):
        o = self.active_object

        if exception is None:
            if o.http_status_code == 404:
                self.profile_exception_event(ERROR_TYPE_404, 'NOT FOUND', as_exception=True)
            return

        self.profile_exception_event(ERROR_TYPE_SERVICE_EXCEPTION, str(exception), as_exception=True)

    def start_external_call(self, call_type, url, host, port=80, caller=''):
        o = self.active_object
        if o.external_call_started:
            return None

        o.create_guid_for_sure()

        if isinstance(call_type, str):
            call_type = call_type.lower()

        if call_type == 'https':
            call_type = REMOTE_CALL_TYPE_HTTPS
        elif call_type == 'http':
            call_type = REMOTE_CALL_TYPE_HTTP

        topology_key = o.agent.gen_new_txid()

        call_hash = self.agent.hash_text('%s (url=%s)' % (caller, url), 'txcall')
        pi = PiExternalCall(o, call_type=call_type, host=host, port=port, text_hash=call_hash)

        if call_type != REMOTE_CALL_TYPE_CUSTOM:
            o.outgoing_key = topology_key
            o.outgoing_sid = o.agent.domain_id
            o.outgoing_agent_id = o.agent.agent_id
            pi.outgoing_remote_call = create_remote_external_capturing_call_pre(call_type, host, port,
                                                                                topology_key, o.agent.domain_id)

        o.set_status(ACTIVE_SERVICE_STATUS_CODE_EXTERNALCALL_EXECUTING)
        o.external_call_name = url
        o.external_call = pi

        o.external_call_started = True
        o.external_call_type = pi.call_type

        self.push_profile(pi)
        return pi

    def end_external_call(self, pi, err, request_key=0, domain_id=0, agent_id=0):
        if pi is None:
            return

        o = self.active_object
        o.external_call_started = False

        if err is not None:
            self.profile_exception_event(ERROR_TYPE_EXTERNAL_CALL_EXCEPTION, str(err))

        if request_key != 0 and domain_id != 0 and agent_id != 0:
            o.outgoing_key = request_key
            o.outgoing_sid = domain_id
            o.outgoing_agent_id = agent_id
            pi.outgoing_remote_call = create_remote_external_capturing_call_post(pi.call_type, pi.host, pi.port,
                                                                                 request_key, domain_id, agent_id)

        pi.end_time = o.get_current_point_time() - pi.start_time
        pi.end_cpu = o.get_method_thread_cpu_time(o.start_cpu_time, pi.start_cpu)
        o.external_call_count += 1
        o.external_call_time += pi.end_time
        o.external_call = None
        o.external_call_type = REMOTE_CALL_TYPE_NONE

        self.pop_profile(pi)
        o.set_status(ACTIVE_SERVICE_STATUS_CODE_RUN)

    def start_conn_open(self, host, port, db):
        msg = 'host={0};port={1};db={2}'.format(host, port, db)
        pi = PiDBMessage(self.active_object, DB_MESSAGE_TYPE_OPEN, msg)

        self.active_object.set_status(ACTIVE_SERVICE_STATUS_CODE_DB_CONNECTING)
        self.push_profile(pi)
        return pi

    def end_conn_open(self, pi, err):
        if pi is None:
            return

        o = self.active_object
        if err is not None:
            self.profile_exception_event(ERROR_TYPE_DB_CONNECTION_FAIL, str(err))

        pi.end_time = o.get_current_point_time() - pi.start_time
        pi.end_cpu = o.get_method_thread_cpu_time(o.start_cpu_time, pi.start_cpu)

        self.pop_profile(pi)
        o.set_status(ACTIVE_SERVICE_STATUS_CODE_RUN)

    def start_conn_close(self):
        pi = PiDBMessage(self.active_object, DB_MESSAGE_TYPE_CLOSE, '')
        return pi

    def end_conn_close(self, pi):
        o = self.active_object
        pi.end_time = o.get_current_point_time() - pi.start_time
        pi.end_cpu = o.get_method_thread_cpu_time(o.start_cpu_time, pi.start_cpu)

        self.add_profile(pi)
        o.set_status(ACTIVE_SERVICE_STATUS_CODE_RUN)

    def add_file_profile(self, name, mode):
        pi = PiFile(self.active_object, name, mode)
        self.add_profile(pi)

    def add_socket_profile(self, host, port, local):
        pi = PiSocket(self.active_object, host, port, local)
        self.add_profile(pi)

    def push_profile(self, pi_data):
        pi_data.index = self.profile_this_idx
        pi_data.parent_index = self.profile_parent_idx
        self.profile_parent_idx = self.profile_this_idx
        self.profile_this_idx += 1

    def push_limited_profile(self, pi_data):
        if self.profile_max_size < self.profile_current_size:
            return False

        self.profile_current_size += 1

        self.push_profile(pi_data)
        return True

    def pop_profile(self, pi_item, drop_profile=False):
        if drop_profile is True:
            self.profile_this_idx = pi_item.index
            self.profile_parent_idx = pi_item.parent_index
            return

        self.profile_parent_idx = pi_item.parent_index
        self.add_and_send(pi_item)

    @staticmethod
    def _process_sql_params(param):
        t = type(param)
        if t is datetime.datetime:
            param = param.strftime('%Y-%m-%d %H:%M:%S')
        elif t is datetime.date:
            param = param.strftime('%Y-%m-%d')
        return param

    def start_query(self, call_info, query, host, port, params=[], query_param_style='format'):
        if len(query) == 0:
            return None

        o = self.active_object
        o.set_status(ACTIVE_SERVICE_STATUS_CODE_SQL_EXECUTING)

        query_hash = self.agent.hash_text(query, 'sql')

        if type(params) is list:
            params = [PiProfiler._process_sql_params(x) for x in params]

        if type(params) is dict:
            params = {
                k.upper(): PiProfiler._process_sql_params(v) for (k, v) in params.items()
            }
            query_param_style = 'pyformat'

        pi = PiSql(o, query_hash, query, params, query_param_style, host, port, call_info)

        o.sql_hash = pi.key
        o.sql_call = pi
        o.running_data_source_name = host + ":" + str(port)
        o.sql_start_time = pi.start_time
        o.running_profile_number_or_n1 = pi.parent_index

        self.push_profile(pi)
        return pi

    def end_query(self, pi, err):
        o = self.active_object

        pi.end_time = o.get_current_point_time() - pi.start_time
        pi.end_cpu = o.get_method_thread_cpu_time(o.start_cpu_time, pi.start_cpu)

        if err is not None:
            self.profile_exception_event(ERROR_TYPE_DB_SQL_EXCEPTION, str(err))

        o.set_status(ACTIVE_SERVICE_STATUS_CODE_RUN)

        o.sql_count += 1
        o.sql_time += pi.end_time

        o.sql_hash = 0
        o.sql_call = None
        o.running_data_source_name = None
        o.sql_start_time = 0
        o.running_profile_number_or_n1 = -1

        min_time = o.agent.app_config.min_sql_time_to_collect
        drop_profile = min_time != 0 and min_time > pi.end_time

        min_time = o.agent.app_config.min_sql_time_to_collect_parameter
        drop_parameter = min_time != 0 and min_time > pi.end_time

        if drop_parameter:
            pi.params = None

        self.pop_profile(pi, drop_profile=drop_profile)

    def start_db_fetch(self, active_object):
        return active_object.set_fetch_status()

    def end_db_fetch(self, pi, o, count):
        o.clear_fetch_status()
        o.fetch_count += count
        pi.count = count
        pi.end_time = o.get_current_point_time() - pi.start_time
        pi.end_cpu = o.get_method_thread_cpu_time(o.start_cpu_time, pi.start_cpu)

        conf_value = self.agent.app_config

        if conf_value.min_sql_fetch_time_to_collect != 0 and conf_value.min_sql_fetch_time_to_collect > pi.end_time:
            return

        self.add_profile(pi)

        if pi.count > conf_value.sql_fetch_warning_count:
            self.profile_warning_event(ERROR_TYPE_TOO_MANY_FETCH)

    def add_profile(self, pi_item):
        pi_item.index = self.profile_this_idx
        pi_item.parent_index = self.profile_parent_idx
        self.profile_this_idx += 1

        self.add_and_send(pi_item)

    def add_and_send(self, pi_item):
        self._profile_entry[self._profile_pos] = pi_item
        self._profile_pos += 1

        if self._profile_pos >= PiProfiler.profile_buffer_size:
            entries = self._profile_entry
            self._profile_entry = [None] * self.profile_max_size
            self._profile_pos = 0

            self.agent.send_profile(self, entries)

    def print_profile(self):
        for child in self._profile_entry:
            if child is None:
                break

            try:
                child.print_description()
            except Exception as e:
                pass

    def to_json_packet(self, profile_entries=None):
        o = self.active_object
        profiles = self._get_profiles(profile_entries)

        return {
            'txid': o.txid,
            'service_hash': o.service_hash,
            'profiles': profiles
        }

    def _get_profiles(self, profile_entries=None):
        profiles = []

        if profile_entries is None:
            profile_entries = self._profile_entry

        for child in profile_entries:
            try:
                if child is None:
                    break

                profiles.append(child.to_json())
            except Exception as e:
                pass

        return profiles
