from big_thing_py.common.common import *

from threading import Thread, Event, Lock, Timer
from queue import Queue, Empty


class ThreadMode(Enum):
    NORMAL = auto()
    TIMER = auto()


class MXThread:
    def __init__(
        self,
        name: str = None,
        target: Callable = None,
        args: Tuple = (),
        kwargs: dict = {},
        daemon: bool = True,
        mode: ThreadMode = ThreadMode.NORMAL,
        interval: float = None,
    ) -> None:
        self._name: str = name
        self._target: Callable = target
        self._args: Tuple = args
        self._kwargs: dict = kwargs
        self._daemon: List[str] = daemon
        self._mode: ThreadMode = mode
        self._thread: Thread = None

        if not target:
            raise Exception('[MXThread] No callback function to run')
        if self._mode == ThreadMode.TIMER and interval is None:
            raise Exception('[MXThread] Thread mode is Timer, but interval is not given...')

        self.set_thread()

    def set_thread(self) -> None:
        if isinstance(self._args, tuple):
            self._args: list = list(self._args)
        else:
            self._args = []

        self._args = tuple(self._args)

        if not self._name:
            self._name = '_'.join(self._target.__name__.split('_')[:-1])

        if self._mode == ThreadMode.NORMAL:
            self._thread = Thread(target=self._target, name=self._name, args=self._args, kwargs=self._kwargs, daemon=self._daemon)
        elif self._mode == ThreadMode.TIMER:
            self._thread = Timer(target=self._target, name=self._name, args=self._args, kwargs=self._kwargs, daemon=self._daemon)
        else:
            raise Exception('[MXThread] Invalid thread mode')

    def start(self) -> None:
        self._thread.start()

    def join(self) -> None:
        self._thread.join()

    def is_alive(self) -> bool:
        return self._thread.is_alive()

    def get_name(self) -> str:
        return self._name

    def get_target_function_name(self) -> str:
        return self._name.split('_')[0]

    def get_target_scenario_name(self) -> str:
        return self._name.split('_')[1]
