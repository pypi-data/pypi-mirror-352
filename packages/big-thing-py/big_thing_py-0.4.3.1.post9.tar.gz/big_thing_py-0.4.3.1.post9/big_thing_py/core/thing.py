from big_thing_py.core.function import MXFunction
from big_thing_py.core.argument import MXArgumentData
from big_thing_py.core.value import MXValue
from big_thing_py.core.service import MXService
from big_thing_py.core.tag import MXTag
from big_thing_py.core.mqtt_message import MXRegisterMessage, MXUnregisterMessage, MXAliveMessage, MXGetHomeMessage
from big_thing_py.core.device_model import Objects as DeviceCategory
from big_thing_py.utils import *
from big_thing_py.core.service_model import SkillValue, SkillFunction
from typing import Coroutine


class MXThing:
    DEFAULT_NAME = 'default_big_thing'

    def __init__(
        self,
        name: str,
        nick_name: str,
        category: DeviceCategory,
        device_type: MXDeviceType,
        service_list: List[MXService],
        alive_cycle: int,
        is_super: bool,
        is_parallel: bool,
        is_ble_wifi: bool = False,
        is_builtin: bool = False,
        is_manager: bool = False,
        is_staff: bool = False,
        is_matter: bool = False,
        desc: str = '',
        version: str = sdk_version(),
        middleware_name: str = '',
    ):
        # base info
        self._name = name
        self._nick_name = nick_name
        self._category = category
        self._device_type = device_type
        self._desc = desc
        self._version = version
        self._service_list = service_list
        self._alive_cycle = alive_cycle
        self._is_super = is_super
        self._is_parallel = is_parallel
        self._is_ble_wifi = is_ble_wifi
        self._is_builtin = is_builtin
        self._is_manager = is_manager
        self._is_staff = is_staff
        self._is_matter = is_matter
        self._middleware_name = middleware_name
        self._request_client_id = ''

        self._last_alive_time = 0
        self._last_alive_check_time = 0
        self._subscribed_topic_set: Set[str] = set()

        for service in self.service_list:
            self.add_service(service)

        if not self._name:
            self._name = self._category.name

        if check_valid_identifier(self._name) == MXErrorCode.INVALID_DATA:
            raise MXValueError(f'name cannot be empty & can only contain alphanumeric characters and underscores. name: {self._name}')
        elif check_valid_identifier(self._name) == MXErrorCode.TOO_LONG_IDENTIFIER:
            raise MXValueError(f'too long identifier. name: {self._name}, length: {len(self._name)}')

        if self._alive_cycle <= 0:
            raise MXValueError(f'alive cycle must be greater than 0')

    def __eq__(self, o: 'MXThing') -> bool:
        instance_check = isinstance(o, MXThing)
        name_check = o._name == self._name
        service_list_check = (o.function_list == self.function_list) and (o.value_list == self.value_list)
        alive_cycle_check = o._alive_cycle == self._alive_cycle
        is_super_check = o.is_super == self.is_super
        is_parallel_check = o.is_parallel == self.is_parallel

        return instance_check and name_check and service_list_check and alive_cycle_check and is_super_check and is_parallel_check

    def __getstate__(self):
        state = self.__dict__.copy()

        del state['_last_alive_time']
        del state['_last_alive_check_time']
        del state['_subscribed_topic_set']

        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

        self._last_alive_time = 0
        self._last_alive_check_time = 0
        self._subscribed_topic_set = set()

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    def get_value(self, value_name: str | SkillValue) -> MXValue:
        if isinstance(value_name, type) and issubclass(value_name, SkillValue):
            value_name = value_name.value_id
        if not isinstance(value_name, str):
            raise MXValueError(f'value_name must be str or SkillValue object')

        for value in self.value_list:
            if value.name == value_name:
                return value

    def get_function(self, function_name: str | SkillFunction) -> MXFunction:
        if isinstance(function_name, type) and issubclass(function_name, SkillFunction):
            function_name = function_name.function_id
        if not isinstance(function_name, str):
            raise MXValueError(f'function_name must be str or SkillFunction object')

        for function in self.function_list:
            if function.name == function_name:
                return function

    def add_service(self, service: MXService) -> 'MXThing':
        service.add_tag(MXTag(name=self._name))
        service.add_tag(MXTag(name=self._category.name))
        service.thing_name = self._name

        if isinstance(service, MXValue):
            value_getter_function = MXFunction(
                name=f'__{service.name}',
                func=service.func,
                return_type=service.type,
                category=service.category,
                tag_list=service.tag_list,
                energy=service.energy,
                desc=service.desc,
                thing_name=service.thing_name,
                middleware_name=service.middleware_name,
                arg_list=[],
            )

            if not service in self.value_list:
                self._service_list.append(service)
            if not value_getter_function in self.function_list:
                self._service_list.append(value_getter_function)
        elif isinstance(service, MXFunction):
            if not service in self.function_list:
                self._service_list.append(service)
        else:
            raise MXTypeError(f'service_list must be list of MXFunction or MXValue object')

        return self

    def dict(self) -> dict:
        return {
            'name': self._name,
            'nick_name': self._nick_name,
            'category': self._category.name,
            'device_type': self.device_type.value,
            'description': self._desc,
            'version': self._version,
            'alive_cycle': self._alive_cycle,
            'is_super': self.is_super,
            'is_parallel': self.is_parallel,
            'is_builtin': self.is_builtin,
            'is_manager': self._is_manager,
            'is_staff': self._is_staff,
            'is_matter': self._is_matter,
            'client_id': self._request_client_id,
            'values': [value.dict() for value in self.value_list],
            'functions': [function.dict() for function in self.function_list],
        }

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
    def function_list(self) -> List[MXFunction]:
        return sorted([service for service in self._service_list if isinstance(service, MXFunction)], key=lambda x: x.name)

    @property
    def value_list(self) -> List[MXValue]:
        return sorted([service for service in self._service_list if isinstance(service, MXValue)], key=lambda x: x.name)

    @property
    def service_list(self) -> List[MXService]:
        return sorted(self._service_list, key=lambda x: x.name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def nick_name(self) -> str:
        return self._nick_name

    @property
    def desc(self) -> str:
        return self._desc

    @property
    def version(self) -> str:
        return self._version

    @property
    def category(self) -> DeviceCategory:
        return self._category

    @property
    def device_type(self) -> MXDeviceType:
        return self._device_type

    @property
    def middleware_name(self) -> str:
        return self._middleware_name

    @property
    def last_alive_time(self) -> float:
        return self._last_alive_time

    @property
    def last_alive_check_time(self) -> float:
        return self._last_alive_check_time

    @property
    def alive_cycle(self) -> float:
        return self._alive_cycle

    @property
    def subscribed_topic_set(self) -> Set[str]:
        return self._subscribed_topic_set

    @property
    def is_super(self) -> bool:
        return self._is_super

    @property
    def is_parallel(self) -> bool:
        return self._is_parallel

    @property
    def is_ble_wifi(self) -> bool:
        return self._is_ble_wifi

    @property
    def is_builtin(self) -> bool:
        return self._is_builtin

    @property
    def is_manager(self) -> bool:
        return self._is_manager

    @property
    def is_staff(self) -> bool:
        return self._is_staff

    @property
    def is_matter(self) -> bool:
        return self._is_matter

    @property
    def request_client_id(self) -> str:
        return self._request_client_id

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @name.setter
    def name(self, name: str) -> None:
        self._name = name
        for service in self.service_list:
            service.thing_name = name

    @nick_name.setter
    def nick_name(self, nick_name: str) -> None:
        self._nick_name = nick_name

    @desc.setter
    def desc(self, desc: str) -> None:
        self._desc = desc

    @version.setter
    def version(self, version: str) -> None:
        self._version = version

    @category.setter
    def category(self, category: DeviceCategory) -> None:
        self._category = category

    @device_type.setter
    def device_type(self, device_type: MXDeviceType) -> None:
        self._device_type = device_type

    @middleware_name.setter
    def middleware_name(self, middleware_name: str) -> None:
        self._middleware_name = middleware_name
        for service in self.service_list:
            service.middleware_name = middleware_name

    @last_alive_time.setter
    def last_alive_time(self, last_alive_time: float) -> None:
        self._last_alive_time = last_alive_time
        self._last_alive_check_time = last_alive_time

    @last_alive_check_time.setter
    def last_alive_check_time(self, last_alive_check_time: float) -> None:
        self._last_alive_check_time = last_alive_check_time

    @alive_cycle.setter
    def alive_cycle(self, alive_cycle: int) -> None:
        self._alive_cycle = alive_cycle

    @subscribed_topic_set.setter
    def subscribed_topic_set(self, subscribed_topic_set: Set[str]) -> None:
        self._subscribed_topic_set = subscribed_topic_set

    @is_super.setter
    def is_super(self, is_super: bool) -> bool:
        self._is_super = is_super

    @is_parallel.setter
    def is_parallel(self, is_parallel: bool) -> bool:
        self._is_parallel = is_parallel

    @is_ble_wifi.setter
    def is_ble_wifi(self, is_ble_wifi: bool) -> bool:
        self._is_ble_wifi = is_ble_wifi

    @is_builtin.setter
    def is_builtin(self, is_builtin: bool) -> bool:
        self._is_builtin = is_builtin

    @is_manager.setter
    def is_manager(self, is_manager: bool) -> bool:
        self._is_manager = is_manager

    @is_staff.setter
    def is_staff(self, is_staff: bool) -> bool:
        self._is_staff = is_staff

    @is_matter.setter
    def is_matter(self, is_matter: bool) -> bool:
        self._is_matter = is_matter

    @request_client_id.setter
    def request_client_id(self, request_client_id: str) -> None:
        self._request_client_id = request_client_id

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    def generate_thing_id(self, name: str, append_mac_address: bool) -> str:
        mac_address = get_mac_address()

        if not check_valid_identifier(name):
            raise MXValueError(f'name cannot be empty & can only contain alphanumeric characters and underscores. name: {self._name}')

        if not append_mac_address:
            return f'{name}'
        elif mac_address:
            return f'{name}_{mac_address}'
        else:
            mac = [random.randint(0x00, 0xFF) for _ in range(6)]
            rand_mac_address = ''.join(map(lambda x: '%02x' % x, mac)).upper()
            return f'{name}_{rand_mac_address}'

    def generate_register_message(self) -> MXRegisterMessage:
        return MXRegisterMessage(thing_name=self.name, payload=self.dict())

    def generate_unregister_message(self) -> MXUnregisterMessage:
        return MXUnregisterMessage(self.name, client_id=self.request_client_id)

    def generate_alive_message(self) -> MXAliveMessage:
        return MXAliveMessage(self.name)

    # need for middleware detect
    def generate_get_home_message(self) -> MXGetHomeMessage:
        return MXGetHomeMessage(self.name)
