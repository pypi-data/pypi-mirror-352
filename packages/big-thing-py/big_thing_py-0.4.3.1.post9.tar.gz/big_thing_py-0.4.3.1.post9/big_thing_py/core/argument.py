from big_thing_py.utils import *
from dataclasses import dataclass


@dataclass
class MXArgumentData:
    # argument: 'MXArgument'
    order: int
    data: MXDataType

    def __post_init__(self):
        if not isinstance(self.order, int):
            raise TypeError(f'order must be int, not {type(self.order)}')

        if not isinstance(self.data, MXDataType):
            raise TypeError(f'data must be {MXDataType}, not {type(self.data)}')

        if MXType.get(type(self.data)) == MXType.STRING and len(self.data) > STRING_VALUE_LIMIT:
            MXLOG_WARN(f'STRING type data beyond `STRING_VALUE_LIMIT`(100) characters will be truncated. Original data: {self.data}')
            self.data = self.data[:STRING_VALUE_LIMIT]


class MXArgument:

    def __init__(self, name: str, type: MXType, bound: Tuple[float, float] = ()) -> None:
        self._name = name
        self._type = type
        self._function_name = None

        # TODO (thsvkd): Not supported (ENUM, LIST, DICT) MXType yet
        if self._type in [MXType.ENUM, MXType.LIST, MXType.DICT]:
            self._type = MXType.STRING

        if self._type in [MXType.STRING, MXType.BINARY]:
            self._min, self._max = -1, -1
        else:
            self._min, self._max = bound
            if self._min >= self._max:
                raise MXValueError('bound must be min < max')

        if check_valid_identifier(self._name) == MXErrorCode.INVALID_DATA:
            raise MXValueError(f'name cannot be empty & can only contain alphanumeric characters and underscores. name: {self._name}')
        elif check_valid_identifier(self._name) == MXErrorCode.TOO_LONG_IDENTIFIER:
            raise MXValueError(f'too long identifier. name: {self._name}, length: {len(self._name)}')

        if self._type in [MXType.UNDEFINED, MXType.VOID] or isinstance(self._type, str):
            raise MXValueError('type cannot be UNDEFINED or VOID or `str` type')

    def __str__(self) -> str:
        return self._name

    def __eq__(self, o: 'MXArgument') -> bool:
        instance_check = isinstance(o, MXArgument)
        name_check = o._name == self._name
        type_check = o._type == self._type
        min_check = o._min == self._min
        max_check = o._max == self._max

        return instance_check and name_check and type_check and min_check and max_check

    def dict(self) -> dict:
        return {'name': self._name, 'type': self._type.value, 'bound': {'min_value': self._min, 'max_value': self._max}}

    # ====================================
    #               _    _
    #              | |  | |
    #   __ _   ___ | |_ | |_   ___  _ __
    #  / _` | / _ \| __|| __| / _ \| '__|
    # | (_| ||  __/| |_ | |_ |  __/| |
    #  \__, | \___| \__| \__| \___||_|
    #   __/ |
    #  |___/
    # ====================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> MXType:
        return self._type

    @property
    def bound(self) -> Tuple[float, float]:
        return self._min, self._max

    @property
    def function_name(self) -> str:
        return self._function_name

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @name.setter
    def name(self, name: str):
        self._name = name

    @type.setter
    def type(self, type: MXType):
        self._type = type

    @bound.setter
    def bound(self, bound: Tuple[float, float]):
        if self._type in [MXType.STRING, MXType.BINARY]:
            self._min, self._max = -1, -1
        else:
            self._min = bound[0]
            self._max = bound[1]

    @function_name.setter
    def function_name(self, function_name: str):
        self._function_name = function_name
