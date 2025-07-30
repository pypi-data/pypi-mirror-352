# -*- coding: utf8 -*-

import os
import subprocess
import sys
import tempfile
import time
import platform
import pathlib
from datetime import datetime
import threading
import traceback

try:  # for Python 2.7
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


enable_diagnostics = os.getenv('JENNIFER_DBG') == '1'
diagnostics_to_file = os.getenv('JENNIFER_LOG_FILE') or None

def print_help():
    print("""
Usage: jennifer-admin run <startup_command ...>
Usage: jennifer-admin runasync <startup_command ...>

startup_command: your wsgi/asgi service startup command and options
""")


def run_master(bin_path, config_path, log_dir, sock_file):

    if sock_file is None:
        return

    arch = {
        'x86_64': 'amd64',
        'x86': '386',
        'arm64': 'arm64',
    }[platform.machine()]

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if not os.path.exists(log_dir):
        _log('ERROR', 'ErrNotExist', log_dir)
        return

    platform_id = sys.platform
    if platform_id == "linux2":
        platform_id = "linux"

    _diag_log('INFO', '[proxy]', sys.platform, arch)
    time.time()
    date_postfix = time.strftime("%Y%m%d")
    log_path = os.path.join(log_dir, 'agent_' + date_postfix + '.log')

    path = os.path.join(bin_path, platform_id, arch, 'jennifer_agent')
    log_stream = open(log_path, 'w+')  # log_path == '/tmp/agent_20220811.log'

    _diag_log('INFO', '[proxy.opening...]', path)
    result = subprocess.Popen(
        [
            path,  # '/mnt/d/.../jennifer/bin/linux/amd64/jennifer_agent'
            config_path,  # '/mnt/d/.../myapp/jennifer.ini'
            sock_file,  # '/tmp/jennifer-1629185873.sock'
        ],
        stdout=log_stream,
        stderr=log_stream,
    )
    _diag_log('INFO', '[proxy.opened]', result)


def run(args, is_async=False):
    start_diagnostics_thread()

    _diag_log('INFO', 'cmdline', sys.argv)
    _diag_log('INFO', 'python version', sys.version)

    if len(args) < 2:
        print_help()
        return

    sock_path = None
    config_file_resolved = False
    wsgi_startup_app_path = args[1]
    config_path = os.environ.get('JENNIFER_CONFIG_FILE')

    if config_path is None:
        print("JENNIFER_CONFIG_FILE is not set")
    else:
        config_path = os.path.join(os.getcwd(), config_path)
        if not os.path.exists(config_path):
            print(config_path + " not exists")
        else:
            config_file_resolved = True

    # uwsgi 또는 gunicorn 등의 실행 파일이 위치한 full path
    if not os.path.dirname(wsgi_startup_app_path):
        for path in os.environ.get('PATH', '').split(os.path.pathsep):
            path = os.path.join(path, wsgi_startup_app_path)
            if os.path.exists(path) and os.access(path, os.X_OK):
                wsgi_startup_app_path = path
                break

    if not os.path.exists(wsgi_startup_app_path):
        raise FileNotFoundError('{0} not found'.format(wsgi_startup_app_path))

    if config_file_resolved:
        try:
            _diag_log('INFO', 'Path-Resolving....')
            jennifer_file_path = __import__('jennifer').__file__
            _diag_log('INFO', 'jennifer module path', jennifer_file_path)
            # print('jennifer_file_path:', jennifer_file_path) # /mnt/d/.../jennifer/__init__.py
        # except ImportError as e:
            # raise e
        except ImportError as e:
            jennifer_file_path = pathlib.Path(__file__).parent.absolute().as_posix()
            _diag_log('INFO', 'jennifer file path', jennifer_file_path)

        root_dir = os.path.dirname(jennifer_file_path)
        bootstrap = os.path.join(root_dir, 'bootstrap')
        # print('jennifer_boot_path', bootstrap) # /mnt/d/.../jennifer/bootstrap

        # 제니퍼 에이전트의 /jennifer/bootstrap 모듈 경로를 "PYTHONPATH"에 추가
        # 왜냐하면, 이후 fork 시 uwsgi/gunicorn 모듈에서 jennifer 모듈을 발견할 수 있어야 하므로!
        python_path = bootstrap
        if 'PYTHONPATH' in os.environ:
            os.environ['OLD_PYTHON_PATH'] = os.environ['PYTHONPATH']
            path = os.environ['PYTHONPATH'].split(os.path.pathsep)
            if bootstrap not in path:
                python_path = os.path.pathsep.join([bootstrap] + path)
        else:
            os.environ['OLD_PYTHON_PATH'] = ""

        os.environ['PYTHONPATH'] = python_path
        _diag_log('INFO', 'PYTHONPATH', python_path)

        time_prefix = time.time()
        py_dbg_mode = int(os.getenv('JENNIFER_PY_DBG') or '0')
        if (py_dbg_mode & 0x02) == 0x02:
            time_prefix = 0

        sock_path = os.path.join(tempfile.gettempdir(), 'jennifer-%d.sock' % time_prefix)
        os.environ['JENNIFER_MASTER_ADDRESS'] = sock_path
        _diag_log('INFO', 'JENNIFER_MASTER_ADDRESS', sock_path)

        if time_prefix == 0:
            sock_path = None

        log_dir = get_ini_value(config_path, 'log_dir', '/tmp')
        os.environ['JENNIFER_LOG_DIR'] = log_dir

        if is_async:
            os.environ['JENNIFER_IS_ASYNC'] = str(is_async)

    if sock_path is None or config_file_resolved == False:
        _diag_log('INFO', 'os.execl', wsgi_startup_app_path, *args[1:])
        os.execl(wsgi_startup_app_path, *args[1:])
    else:
        _diag_log('INFO', 'os.forking...')
        pid = os.fork()
        if pid > 0:  # pid == child process id
                     # running code in current(parent-of-child) process
            _diag_log('INFO', 'Waiting for run_master', pid)
            os.waitpid(pid, 0)  # run_master 함수가 반환될 때까지 대기
            _diag_log('INFO', 'Execl: ', wsgi_startup_app_path)
            os.execl(wsgi_startup_app_path, *args[1:])
        else:  # child process - 최초 jennifer-admin run uwsgi... 실행 시 진입
            _diag_log('INFO', '[run-proxy]', '(ppid:', str(os.getppid()) + ')', os.path.join(root_dir, 'bin'), config_path, log_dir, sock_path)
            run_master(os.path.join(root_dir, 'bin'), config_path, log_dir, sock_path)


if __name__ == '__main__':
    run(sys.argv[1:])
    exit(-1)


def get_ini_value(config_path, key_name, default_value):
    config_file = open(config_path, 'r')

    for line in config_file.readlines():
        items = line.split('=')
        if len(items) != 2:
            continue

        key = items[0].strip(' ')
        value = items[1].strip(' ').rstrip()

        if key != key_name:
            continue

        return value

    return default_value


def format_time(time_value):
    return time_value.strftime("[%Y-%m-%d %H:%M:%S]")


def _log(level, *args):
    current_time = format_time(datetime.now())
    print(current_time, '[' + str(os.getpid()) + ']', level, '[jennifer]', args)


def _diag_log(level, *args):
    if enable_diagnostics is False:
        return

    time_now = datetime.now()
    time_column = format_time(time_now)

    if diagnostics_to_file is not None:
        log_file_path = os.path.join(diagnostics_to_file, "agent_diag_" + str(os.getpid()) + ".log")
        with open(log_file_path, 'a') as log_file:
            log_file.write(time_column + ' ' + str(args) + '\n')

    print(time_column, '[' + str(os.getpid()) + ']', level, '[jennifer]', args)


def start_diagnostics_thread():
    if os.getenv('JENNIFER_DBG') != '2':
        return

    _diag_log('INFO', 'Activate start_diagnostics_thread', 'ppid:', os.getppid())
    diag_thread = threading.Thread(target=diagnostics_startup_thread)
    diag_thread.setName('jennifer-diagnostics')
    diag_thread.setDaemon(True)
    try:
        diag_thread.start()
    except:
        _diag_log('ERROR', 'Failed to start diagnostics_startup_thread')


def diagnostics_startup_thread():
    while True:
        try:
            dump_thread_stack()
        except Exception as e:
            _diag_log('ERROR', 'diag-thread', e)
            break
        time.sleep(1)


def dump_thread_stack():
    current_thread = threading.current_thread()

    for t in threading.enumerate():
        if t is current_thread:
            continue

        frame = sys._current_frames().get(t.ident)
        if frame is None:
            continue

        try:
            formatted = traceback.format_stack(frame)
            stack = ''.join(formatted)
        except Exception as e:
            stack = "call_stack: " + str(e)
        print('thread:', t.name, t.ident, stack)
