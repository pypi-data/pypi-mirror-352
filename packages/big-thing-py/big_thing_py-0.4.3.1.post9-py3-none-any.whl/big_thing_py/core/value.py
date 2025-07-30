import asyncio
from big_thing_py.core.service import *
from big_thing_py.core.request import *
from big_thing_py.core.service_model import SkillValue
from big_thing_py.core.service_model import Objects as Skill


class MXValue(MXService):

    def __init__(
        self,
        func: Callable,
        tag_list: List[MXTag],
        type: Optional[MXType] = None,
        category: Optional[SkillValue] = None,
        cycle: float = 0,
        bound: Optional[Tuple[float, float]] = None,
        name: str = '',
        energy: float = 0,
        desc: str = '',
        thing_name: str = '',
        middleware_name: str = '',
        format: str = '',
    ) -> None:
        super().__init__(
            func=func,
            tag_list=tag_list,
            name=name,
            category=category,
            energy=energy,
            desc=desc,
            thing_name=thing_name,
            middleware_name=middleware_name,
        )

        # Check type and bound
        if self._category != None:
            if type:
                MXLOG_INFO('`type`, `bound` parameter will be ignored because category is given')

            self._type = normalize_mx_type(self._category.value_type.type)
            self._min, self._max = normalize_bound(self._type, self._category.value_type.bound)
        else:
            if not type:
                raise MXValueError('`type` must be given when category is not given')

            self._type = normalize_mx_type(type)
            self._min, self._max = normalize_bound(self._type, bound)

        # Check type is valid
        if self._type in [MXType.UNDEFINED, MXType.VOID] or isinstance(self._type, str):
            raise MXValueError('`type` cannot be UNDEFINED or VOID type or `str` type')

        # Check min < max
        if not self._type in [MXType.STRING, MXType.BINARY] and self._min >= self._max:
            raise MXValueError('`bound` must be min < max when type is not STRING or BINARY')

        # Check cycle is valid
        if (cycle < 0) if cycle != None else False:
            raise MXValueError('`cycle` must be >= 0')  # if cycle is 0, it means that the value is event-based
        self._cycle = cycle

        # Check format is string
        if not isinstance(format, str):
            raise MXValueError('`format` must be str')
        self._format = format

        # Check callback function is valid
        if len(get_function_info(self._func)['args']) > 0 or get_function_info(self._func)['return_type'] == None:
            raise MXValueError('callback function must not have any argument and must return value')

        self._last_value: Optional[Union[float, str, bool]] = None
        self._last_update_time: float = 0
        self._binary_sending: bool = False

        self.is_initialized = False

    def __eq__(self, o: 'MXValue') -> bool:
        instance_check = isinstance(o, MXValue)
        type_check = o._type == self._type
        bound_check = o._max == self._max and o._min == self._min
        format_check = o._format == self._format
        cycle_check = o._cycle == self._cycle

        return super().__eq__(o) and instance_check and type_check and bound_check and format_check and cycle_check

    def __getstate__(self):
        state = super().__getstate__()

        state['_type'] = self._type
        state['_min'] = self._min
        state['_max'] = self._max
        state['_cycle'] = self._cycle
        state['_format'] = self._format

        del state['_last_value']
        del state['_last_update_time']
        del state['_binary_sending']

        return state

    def __setstate__(self, state):
        super().__setstate__(state)

        self._type = state['_type']
        self._min = state['_min']
        self._max = state['_max']
        self._cycle = state['_cycle']
        self._format = state['_format']

        self._last_value = None
        self._last_update_time = 0
        self._binary_sending = False

    async def async_update(self, set_value: MXDataType = None) -> MXDataType:
        try:
            if not set_value is None:
                new_value = set_value
            else:
                if asyncio.iscoroutinefunction(self._func):
                    new_value = await self._func()
                else:
                    new_value = self._func()

            if new_value is None:
                MXLOG_ERROR(f'Failed to get value from callback function {self._func.__name__}')
                return None

            self._last_update_time = get_current_datetime()

            if self._last_value != new_value:
                self._last_value = new_value
                return new_value
            else:
                return None
        except Exception as e:
            print_error(e)
        finally:
            if not self.is_initialized:
                self.is_initialized = True

    def sync_update(self, set_value: MXDataType = None) -> MXDataType:
        try:
            if not set_value is None:
                new_value = set_value
            else:
                new_value = self._func()

            if new_value is None:
                raise MXValueError('return value of Value callback function is None')

            self._last_update_time = get_current_datetime()

            if self._last_value != new_value:
                self._last_value = new_value
                return new_value
            else:
                return None
        except Exception as e:
            print_error(e)
        finally:
            if not self.is_initialized:
                self.is_initialized = True

    def dict(self) -> dict:
        return {
            'name': self._name,
            'category': self._category.value_id if self._category else None,
            'description': self._desc,
            'tags': [tag.dict() for tag in self._tag_list],
            'type': self._type.value,
            'bound': {'min_value': self._min, 'max_value': self._max},
            'format': self._format,
        }

    def publish_dict(self) -> dict:
        if isinstance(self._last_value, BinaryBase64):
            return {'type': self._type.value, 'value': str(self._last_value)}
        else:
            return {'type': self._type.value, 'value': self._last_value}

    def generate_value_publish_message(self) -> MXValuePublishMessage:
        return MXValuePublishMessage(self.name, self.thing_name, self.publish_dict())

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
    def type(self) -> MXType:
        return self._type

    @property
    def bound(self) -> Tuple[float, float]:
        return (self._min, self._max)

    @property
    def max(self) -> float:
        return self._max

    @property
    def min(self) -> float:
        return self._min

    @property
    def cycle(self) -> float:
        return self._cycle

    @property
    def format(self) -> str:
        return self._format

    @property
    def last_value(self) -> float:
        return self._last_value

    @property
    def last_update_time(self) -> float:
        return self._last_update_time

    @property
    def binary_sending(self) -> bool:
        return self._binary_sending

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @type.setter
    def type(self, type: MXType) -> None:
        self._type = type

    @bound.setter
    def bound(self, bound: Tuple[float, float]) -> None:
        if self._type in [MXType.STRING, MXType.BINARY]:
            self._min, self._max = -1, -1
        else:
            self._min = bound[0]
            self._max = bound[1]

    @max.setter
    def max(self, max: float) -> None:
        self._max = max

    @min.setter
    def min(self, min: float) -> None:
        self._min = min

    @cycle.setter
    def cycle(self, cycle: float) -> None:
        self._cycle = cycle

    @format.setter
    def format(self, format: str) -> None:
        self._format = format

    @last_value.setter
    def last_value(self, last_value: Union[float, str, bool]) -> None:
        self._last_value = last_value

    @last_update_time.setter
    def last_update_time(self, last_update_time: float) -> None:
        self._last_update_time = last_update_time

    @binary_sending.setter
    def binary_sending(self, binary_send: bool) -> bool:
        self._binary_sending = binary_send
