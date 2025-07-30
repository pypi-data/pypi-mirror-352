import os
from datetime import datetime

DEFAULT_CONFIG = """[JENNIFER]

server_address = 127.0.0.1
server_port = 5000
domain_id = 1000
inst_id = -1

# log_dir = /tmp
# service_dump_dir = /tmp
"""


def print_help():
    print("""
Usage: jennifer generate-config [output_file]

output_file: default output file name is jennifer.ini
""")


def generate_config(args):
    if len(args) < 2:
        filename = 'jennifer.ini'
    else:
        filename = args[1]
        if filename in ['--help', '-h']:
            print_help()
            return

    if os.path.exists(filename):
        _log('INFO', '%s is already exists.' % filename)
        return

    working_directory = os.getcwd()
    with open(os.path.join(working_directory, filename), 'w') as f:
        f.write(DEFAULT_CONFIG)
        f.flush()


def format_time(time_value):
    return time_value.strftime("[%Y-%m-%d %H:%M:%S]")


def _log(level, *args):
    current_time = format_time(datetime.now())
    print(current_time, '[' + str(os.getpid()) + ']', level, '[jennifer]', args)
