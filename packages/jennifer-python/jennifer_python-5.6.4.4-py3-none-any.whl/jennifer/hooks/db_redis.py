import os

from jennifer.agent import jennifer_agent
import json
from jennifer.pconstants import *
from .util import _log, VersionInfo

__hooking_module__ = 'redis'
__minimum_python_version__ = VersionInfo("2.7.0")
_original_redis_execute_command = None
_original_redis_ctor = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def import_module():
    return __import__(__hooking_module__)


def format_command(max_length, *args):
    cmd = str(args[0])
    parameters = [cmd]

    arg_length = len(cmd)
    for arg in args[1:]:
        max_length -= arg_length
        arg_text = str(arg)[0:max_length]
        parameters.append(arg_text)
        arg_length += len(arg_text)

        if arg_length >= max_length:
            break

    return ' [REDIS] ' + ' '.join(parameters)


def wrap_init_command(origin):

    def handler(*args, **kwargs):
        err = None

        try:
            origin(*args, **kwargs)
        except Exception as e:
            err = e

        this_instance = None
        if len(args) > 0:
            this_instance = args[0]

        try:
            if this_instance is not None:
                host = kwargs.get('host', None)
                port = kwargs.get('port', None)
                unix_path = kwargs.get('unix_socket_path', None)

                if unix_path is not None:
                    host = 'localhost'
                    port = 6379

                this_instance.__host = host
                this_instance.__port = port

        except Exception as e:
            _log('ERROR', 'db.redis.init', e)

        if err is not None:
            raise err

    return handler


def wrap_execute_command(origin):

    def handler(self, *args, **kwargs):
        o = None
        pi = None
        ret = None

        try:
            agent = jennifer_agent()
            if agent is not None:
                o = agent.current_active_object()
                if o is not None:
                    if agent.app_config.redis_as_external_call is False:
                        message = format_command(agent.app_config.profile_method_parameter_value_length, *args)
                        o.profiler.add_message(message)
                    else:
                        pi = o.profiler.start_external_call(
                            call_type=REMOTE_CALL_TYPE_REDIS,
                            url='redis://' + self.__host + ':' + str(self.__port),
                            host=self.__host,
                            port=self.__port,
                            caller='Redis.execute_command')

        except Exception as e:
            _log('ERROR', 'db.redis.exec', e)

        err = None

        try:
            ret = origin(self, *args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi is not None:
                o.profiler.end_external_call(pi, err)
        except:
            pass

        if err is not None:
            raise err

        return ret

    return handler


def unhook(redis_module):
    global _original_redis_execute_command
    if _original_redis_execute_command is not None:
        redis_module.Redis.execute_command = _original_redis_execute_command
        redis_module.Redis.__init__ = _original_redis_ctor


def hook(redis_module):
    global _original_redis_execute_command
    global _original_redis_ctor

    if 'wrap_execute_command.' in str(redis_module.Redis.execute_command):
        return False

    global __target_version
    __target_version = redis_module.__version__

    _original_redis_execute_command = redis_module.Redis.execute_command
    _original_redis_ctor = redis_module.Redis.__init__

    redis_module.Redis.execute_command = wrap_execute_command(redis_module.Redis.execute_command)
    redis_module.Redis.__init__ = wrap_init_command(redis_module.Redis.__init__)
    return True
