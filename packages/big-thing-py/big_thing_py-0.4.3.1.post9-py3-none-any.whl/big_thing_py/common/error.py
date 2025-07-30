from enum import Enum, auto


class MXErrorCode(Enum):
    NO_ERROR = 0
    FAIL = -1
    PERMISSION = -2
    TIMEOUT = -3
    DUPLICATE = -4
    TARGET_NOT_FOUND = -5
    REQUESTER_NOT_FOUND = -6
    INVALID_REQUEST = -7
    INVALID_DATA = -8
    INVALID_DESTINATION = -9
    TOO_LONG_IDENTIFIER = -10
    EXECUTE_FAIL = -11
    EXECUTE_TIMEOUT = -12
    EXECUTE_PARALLEL = -13
    EXECUTE_DUPLICATE = -14
    EXECUTE_ARG_FAIL = -15
    VALUE_ERROR = -16
    TYPE_ERROR = -18
    NOT_FOUND_ERROR = -19
    CONNECTION_ERROR = -20
    NOT_SUPPORTED = -21

    UNDEFINED = 'undefined'

    @classmethod
    def to_mx_error_code(cls, type: int):
        if type is not None:
            for mx_error_code in MXErrorCode:
                if mx_error_code.value == type:
                    return mx_error_code
        else:
            return MXErrorCode.get(type)

    @classmethod
    def get(cls, type: int) -> 'MXErrorCode':
        try:
            if type is not None:
                for mx_error_type in MXErrorCode:
                    if mx_error_type.value == type:
                        return mx_error_type
                return cls.UNDEFINED
            else:
                return MXErrorCode.get(type)
        except Exception:
            return cls.UNDEFINED

    def __str__(self):
        return self.name


class MXError(Exception):
    def __init__(self, error_code: MXErrorCode, *args: object, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.error_code: MXErrorCode = error_code


class MXFailError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.FAIL, *args, **kwargs)


class MXPermissionError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.PERMISSION, *args, **kwargs)


class MXTimeoutError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.TIMEOUT, *args, **kwargs)
        self.error_code = MXErrorCode.TIMEOUT


class MXDuplicatedError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.DUPLICATE, *args, **kwargs)


class MXTargetNotFound(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.TARGET_NOT_FOUND, *args, **kwargs)


class MXRequesterNotFound(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.REQUESTER_NOT_FOUND, *args, **kwargs)


class MXNotSupportedError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.NOT_SUPPORTED, *args, **kwargs)


class MXInvalidRequestError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.INVALID_REQUEST, *args, **kwargs)


class MXValueError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.VALUE_ERROR, *args, **kwargs)


class MXTypeError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.TYPE_ERROR, *args, **kwargs)


class MXNotFoundError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.NOT_FOUND_ERROR, *args, **kwargs)


class MXConnectionError(MXError):
    def __init__(self, *args: object, **kwargs: dict) -> None:
        super().__init__(MXErrorCode.CONNECTION_ERROR, *args, **kwargs)
