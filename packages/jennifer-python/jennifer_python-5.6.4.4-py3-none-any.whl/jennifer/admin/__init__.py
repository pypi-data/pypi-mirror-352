#!/usr/bin/env python
import os
import sys
from datetime import datetime

try:  # for Python 2.7
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

try:
    from .generate_config import generate_config
    from .run import run
except ValueError:  # for Python 2.7 (direct run in command line)
    from generate_config import generate_config
    from run import run
except ImportError:  # for Python 3.x
    from generate_config import generate_config
    from run import run


def print_help():
    print("""
Usage: jennifer-admin <command> [options]

JENNIFER 5 python agent 

Commands:
    generate-config
    version
    run
    runasync
""")


def main():
    if len(sys.argv) < 2:
        print_help()
        exit()

    command = sys.argv[1]
    os.environ['JENNIFER_PYTHON_PATH'] = sys.executable

    try:

        if command == 'generate-config':
            generate_config(sys.argv[1:])
            exit(-1)
        elif command == 'version':
            import jennifer
            print('JENNIFER Python(%s)' % jennifer.__version__)
        elif command == 'run':
            run(sys.argv[1:], is_async=False)
        elif command == 'runasync':
            run(sys.argv[1:], is_async=True)
        else:
            print_help()

    except(EnvironmentError, FileNotFoundError) as e:
        print('ERROR', "{0}\n\ntype 'jennifer-admin {1} help' for help".format(str(e), command))


if __name__ == '__main__':
    main()
    exit(-1)


def format_time(time_value):
    return time_value.strftime("[%Y-%m-%d %H:%M:%S]")


def _log(level, *args):
    current_time = format_time(datetime.now())
    print(current_time, '[' + str(os.getpid()) + ']', level, '[jennifer]', args)
