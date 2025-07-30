from aenum import IntEnum, StrEnum


class MXStrEnum(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __new__(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value == value:
                    return member

        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj


class MXIntEnum(IntEnum):
    def _generate_next_value_(name, start, count, last_values):
        return count

    def __new__(cls, value):
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member

        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj
