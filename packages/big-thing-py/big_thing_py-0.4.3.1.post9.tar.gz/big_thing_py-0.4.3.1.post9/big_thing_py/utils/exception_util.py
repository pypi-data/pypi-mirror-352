from big_thing_py.utils.log_util import *

import traceback


def print_error(e: Exception):
    traceback_msg = traceback.format_exc()
    MXLOG_DEBUG(f'Traceback message : {traceback_msg}\nError: {e}', 'red')
