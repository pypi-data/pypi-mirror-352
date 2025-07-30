from big_thing_py.core.argument import MXArgument
from big_thing_py.utils.common_util import MXType, MXDataType, MXTypeError, BinaryBase64
from big_thing_py.utils.log_util import *

from typing import List, Union
import sys


def compare_arg_list(arg_list1: List[Union[MXArgument, MXDataType]], arg_list2: List[Union[MXArgument, MXDataType]]):
    def convert_arg(arg: MXDataType) -> MXArgument:
        if isinstance(arg, bool):
            return MXArgument(name='converted_argument', type=MXType.BOOL, bound=(0, 1))
        elif isinstance(arg, int):
            return MXArgument(name='converted_argument', type=MXType.INTEGER, bound=(-sys.maxsize - 1, sys.maxsize))
        elif isinstance(arg, float):
            return MXArgument(name='converted_argument', type=MXType.DOUBLE, bound=(-sys.maxsize - 1, sys.maxsize))
        elif isinstance(arg, str):
            if BinaryBase64.is_base64(arg):
                return MXArgument(name='converted_argument', type=MXType.BINARY)
            else:
                return MXArgument(name='converted_argument', type=MXType.STRING)
        else:
            raise MXTypeError(f'arg must be {MXDataType}: {arg}')

    def convert_arg_list(arg_list: List[Union[MXArgument, MXDataType]]) -> List[MXType]:

        # In case of arg_list is list of MXArgument
        if isinstance(arg_list, list) and all([isinstance(arg, MXArgument) for arg in arg_list]):
            return [arg.type for arg in arg_list]
        # In case of arg_list is list of MXDataType
        elif isinstance(arg_list, list) and all([isinstance(arg, MXDataType) for arg in arg_list]):
            return [convert_arg(arg).type for arg in arg_list]
        else:
            raise MXTypeError(f'arg_list must be list of MXArgument or list of {MXDataType}: {arg_list}')

    arg_type_list1 = convert_arg_list(arg_list1)
    arg_type_list2 = convert_arg_list(arg_list2)

    if len(arg_type_list1) != len(arg_type_list2):
        MXLOG_CRITICAL(f'Not matched arg_list length: {len(arg_type_list1)} != {len(arg_type_list2)}')
        return False

    for arg_type1, arg_type2 in zip(arg_type_list1, arg_type_list2):
        if arg_type1 in [MXType.INTEGER, MXType.DOUBLE] and arg_type2 in [MXType.INTEGER, MXType.DOUBLE]:
            pass
        elif arg_type1 != arg_type2:
            MXLOG_CRITICAL(f'Not matched arg_list type: {arg_type1} != {arg_type2}')
            return False
    else:
        return True
