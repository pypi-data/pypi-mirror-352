from typing import *
from typing_extensions import override, overload
from termcolor import *
from abc import *
from enum import Enum, auto


EMPTY_JSON = {}
THREAD_TIME_OUT = 0.01


class TimeFormat(Enum):
    DATETIME1 = auto()
    DATETIME2 = auto()
    DATETIME3 = auto()
    DATE = auto()
    TIME = auto()
    UNIXTIME = auto()


class MXPrintMode(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()

    UNDEFINED = auto()
    FULL = auto()
    ABBR = auto()
    SKIP = auto()

    @classmethod
    def get(cls, name: str) -> 'MXPrintMode':
        try:
            return cls[name.upper()]
        except Exception:
            return cls.UNDEFINED


class Direction(Enum):
    PUBLISH = 'PUBLISH'
    RECEIVED = 'RECEIVED'


class PrintTag:
    # MQTT protocol
    GOOD = '[%-30s]' % colored('✔✔✔', 'green')
    DUP = '[%-30s]' % colored('DUP✔', 'green')
    ERROR = '[%-30s]' % colored('✖✖✖', 'red')

    CONNECT = '[%-30s]' % colored('-> CONNECT', 'blue')
    DISCONNECT = '[%-30s]' % colored('-> DISCONNECT', 'blue')

    SUBSCRIBE = '[%-30s]' % colored('-> SUBSCRIBE', 'white')
    UNSUBSCRIBE = '[%-30s]' % colored('-> UNSUBSCRIBE', 'white')
