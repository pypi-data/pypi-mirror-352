import os
import sys
from jennifer.agent import jennifer_agent
from .util import _log

# config.address == /tmp/jennifer-...sock
# config.log_dir == /tmp


def _hook_uncaught_exception(exc_type, value, exc_tb):
    import traceback
    _log('ERROR', 'uncaught', exc_type, value, exc_tb)
    traceback.print_tb(exc_tb)


try:
    if os.getenv('JENNIFER_PY_DBG'):
        sys.excepthook = _hook_uncaught_exception
except:
    pass


def init():
    jennifer_agent()
