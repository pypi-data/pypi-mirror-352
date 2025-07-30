from jennifer.pconstants import *


class OutgoingRemoteCallInfo:
    def __init__(self, call_type=REMOTE_CALL_TYPE_NONE, host='', port=0,
                 request_hash=0, recv_sid=0, recv_oid=0, desc_hash=0):
        self.call_type = call_type
        self.host = host
        self.port = port
        self.request_hash = request_hash
        self.recv_sid = recv_sid
        self.recv_oid = recv_oid
        self.desc_hash = desc_hash

    def to_dict(self):
        return {
            'call_type': self.call_type,
            'ip_port': {'host': self.host, 'port': self.port},
            'request_hash': int(self.request_hash),
            'recv_sid': int(self.recv_sid),
            'recv_oid': int(self.recv_oid),
            'desc_hash': int(self.desc_hash),
        }

    def to_string(self):
        return 'OutCallInfo: %s, %s, %s' % (self.get_remote_name(), self.host, self.port)

    def get_remote_name(self):
        if self.call_type == REMOTE_CALL_TYPE_MYSQL:
            return "MySQL"
        if self.call_type == REMOTE_CALL_TYPE_ORACLE:
            return "Oracle"

        return "Not-supported-type"


def create_remote_ip_port_capturing_call(call_type, host, port):
    if isinstance(host, list):
        if len(host) == 0:
            return OutgoingRemoteCallInfo(call_type, "127.0.0.1", 27017)
        host = host[0]

    return _create_remote_capturing_call(call_type, host, port)


def _create_remote_capturing_call(call_type, host, port, topology_key=0, domain_id=0, agent_id=0):
    found = host.find('//')

    if found != -1:
        host = host[found + 2:]

        found = host.rfind(':')
        if found != -1:
            host = host[:found]

    return OutgoingRemoteCallInfo(call_type, host, port, topology_key, domain_id, agent_id)


def create_remote_external_capturing_call_pre(call_type, host, port, topology_key, domain_id):
    return _create_remote_capturing_call(call_type, host, port, topology_key, domain_id)


def create_remote_external_capturing_call_post(call_type, host, port, topology_key, domain_id, agent_id):
    return _create_remote_capturing_call(call_type, host, port, topology_key, domain_id, agent_id)
