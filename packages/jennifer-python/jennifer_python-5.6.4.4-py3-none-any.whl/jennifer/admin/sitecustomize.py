
import os
import tempfile
import time
from datetime import datetime
import platform
import sys
import subprocess
import traceback


enable_diagnostics = os.getenv('JENNIFER_DBG') == '1'
diagnostics_to_file = os.getenv('JENNIFER_LOG_FILE') or None
root_dir = os.path.dirname(os.path.dirname(__file__))


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

    _diag_log('INFO', '[fork]', sys.platform, arch)
    time.time()
    date_postfix = time.strftime("%Y%m%d")
    log_path = os.path.join(log_dir, 'agent_' + date_postfix + '.log')

    path = os.path.join(bin_path, platform_id, arch, 'jennifer_agent')
    log_stream = open(log_path, 'w+')  # log_path == '/tmp/agent_20220811.log'

    _diag_log('INFO', '[fork.opening...]', path)
    result = subprocess.Popen(
        [
            path,  # '/mnt/d/.../jennifer/bin/linux/amd64/jennifer_agent'
            config_path,  # '/mnt/d/.../myapp/jennifer.ini'
            sock_file,  # '/tmp/jennifer-1629185873.sock'
        ],
        stdout=log_stream,
        stderr=log_stream,
    )
    _diag_log('INFO', '[fork.opened]', result)


def check_connection_info_from_environment(config_path, time_prefix):
    if len(config_path) == 0:
        domain_id = os.environ.get("ARIES_DOMAIN_ID")
        inst_id = os.environ.get("ARIES_INST_ID")
        server_address = os.environ.get("ARIES_SERVER_ADDRESS")
        server_port = os.environ.get("ARIES_SERVER_PORT")

        if domain_id is None or inst_id is None or server_address is None or server_port is None:
            return config_path

        ini_path = os.path.join(tempfile.gettempdir(), 'jennifer-temp-config-%d.ini' % time_prefix)
        if time_prefix != 0:
            if os.path.exists(ini_path):
                os.remove(ini_path)

            with open(ini_path, "w") as ini_file:
                ini_file.write("[JENNIFER]" + os.linesep + os.linesep)
                ini_file.close()

        os.environ.setdefault("JENNIFER_CONFIG_FILE", ini_path)
        return ini_path

    return config_path

def run_master_process():
    time_prefix = time.time()
    py_dbg_mode = int(os.getenv('JENNIFER_PY_DBG') or '0')
    if (py_dbg_mode & 0x02) == 0x02:
        time_prefix = 0

    config_path = os.environ.get('JENNIFER_CONFIG_FILE') or ''
    config_path = check_connection_info_from_environment(config_path, time_prefix)

    if config_path == '' or not os.path.exists(config_path):
        raise FileNotFoundError('[JENNIFER_CONFIG_FILE] ' + config_path + " not exists")

    log_dir = os.environ.get('JENNIFER_LOG_DIR') or '/tmp'
    os.environ['JENNIFER_LOG_DIR'] = log_dir

    master_path = os.path.join(root_dir, 'bin')
    sock_path = os.path.join(tempfile.gettempdir(), 'jennifer-%d.sock' % time_prefix)
    os.environ['JENNIFER_MASTER_ADDRESS'] = sock_path

    if time_prefix == 0:
        sock_path = None

    if os.path.exists(master_path):
        run_master(master_path, config_path, log_dir, sock_path)


def load_jennifer():
    jennifer_path = None

    try:
        jennifer = __import__('jennifer')
    except ImportError as e:
        jennifer_path = os.path.abspath(os.path.join(root_dir, '..'))
        sys.path.append(jennifer_path)

        try:
            jennifer = __import__('jennifer')
        except Exception as critical_error:
            _diag_log('ERROR', 'Import Error(load)', critical_error)

    if os.environ.get('JENNIFER_MASTER_ADDRESS') is None:
        _diag_log('ERROR', 'Not Found: JENNIFER_MASTER_ADDRESS')
    else:
        try:
            _diag_log('INFO',sys.version, 'startup.init(load)', jennifer_path)  # sys.argv == ''
            jennifer.startup.init()
        except Exception as e:
            _diag_log('ERROR','site_customize(load)', e)
            if enable_diagnostics:
                traceback.print_exc()


if __name__ == 'sitecustomize':
    run_master_process()

    os.environ['JENNIFER_PYTHON_PATH'] = sys.executable
    load_jennifer()
