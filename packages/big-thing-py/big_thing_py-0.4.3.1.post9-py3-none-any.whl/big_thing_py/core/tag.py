from big_thing_py.utils import *


class MXTag:
    def __init__(self, name: str):
        self._name: str = name

        if check_valid_identifier(self._name) == MXErrorCode.INVALID_DATA:
            raise MXValueError(f'name cannot be empty & can only contain alphanumeric characters and underscores. name: {self._name}')
        elif check_valid_identifier(self._name) == MXErrorCode.TOO_LONG_IDENTIFIER:
            raise MXValueError(f'too long identifier. name: {self._name}, length: {len(self._name)}')

    def __eq__(self, o: 'MXTag') -> bool:
        name_check = o._name == self._name

        return isinstance(o, MXTag) and name_check

    def __str__(self) -> str:
        return self._name

    def dict(self):
        return {'name': self._name}

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
    def name(self):
        return self._name

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @name.setter
    def name(self, name):
        self._name = name
