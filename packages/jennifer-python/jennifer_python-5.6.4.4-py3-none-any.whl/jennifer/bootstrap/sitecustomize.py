import os
import sys
import traceback
from os import path
from datetime import datetime

_debug_mode = os.getenv('JENNIFER_PY_DBG')
enable_diagnostics = os.getenv('JENNIFER_DBG') == '1'
diagnostics_to_file = os.getenv('JENNIFER_LOG_FILE') or None


def format_time(time_value):
    return time_value.strftime("[%Y-%m-%d %H:%M:%S]")


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


jennifer_path = None
jennifer = None

try:
    jennifer = __import__('jennifer')
except ImportError as e:
    jennifer_path = path.abspath(path.join(path.dirname(__file__), '..', '..'))
    sys.path.append(jennifer_path)

    try:
        jennifer = __import__('jennifer')
    except Exception as critical_error:
        _diag_log('ERROR', 'Import Error(bootstrap)', critical_error)

if jennifer is None:
    _diag_log('ERROR', 'JENNIFER module not imported')
else:
    if os.environ.get('JENNIFER_MASTER_ADDRESS') is None:
        _diag_log('ERROR', 'Not Found: JENNIFER_MASTER_ADDRESS')
    else:
        try:
            _diag_log('INFO', 'startup.init(bootstrap)', jennifer_path)
            jennifer.startup.init()
        except Exception as e:
            _diag_log('ERROR', 'site_customize(bootstrap)', e)
            if _debug_mode:
                traceback.print_exc()
