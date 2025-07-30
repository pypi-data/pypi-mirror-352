from big_thing_py.manager.manager_common import *
from big_thing_py.core.thing import *


class MXStaffThing(MXThing, metaclass=ABCMeta):

    def __init__(
        self,
        uid: str,
        nick_name: str,
        category: DeviceCategory,
        device_type: MXDeviceType,
        desc: str,
        version: str,
        service_list: List[MXService],
        alive_cycle: int,
        is_parallel: bool,
        is_matter: bool,
        vendor_id: str,
        product_id: str,
        info: dict,
        manager_name: str,
    ):
        super().__init__(
            name=category.name + '__' + thing_name_uid_convert(uid, ThingNameRawIDConvertMode.RawDeviceIDToThingName),
            nick_name=nick_name,
            desc=desc,
            category=category,
            device_type=device_type,
            version=version,
            service_list=service_list,
            alive_cycle=alive_cycle,
            is_super=False,
            is_parallel=is_parallel,
            is_builtin=False,
            is_manager=False,
            is_staff=True,
            is_matter=is_matter,
        )
        self._is_alive = False

        self._uid = uid
        self._vendor_id = vendor_id
        self._product_id = product_id
        self._info = info
        self._manager_name = manager_name

        self._default_tag_list: List[MXTag] = [
            MXTag(tag if check_valid_identifier(tag) == MXErrorCode.NO_ERROR else convert_to_valid_string(tag))
            for tag in [
                self._name,
                # self._nick_name,
            ]
            if tag
        ]

    def __eq__(self, o: 'MXStaffThing') -> bool:
        instance_check = isinstance(o, MXStaffThing)
        staff_thing_name_check = o._name == self._name

        # return super().__eq__(o) and instance_check and staff_thing_id_check
        return instance_check and staff_thing_name_check

    def add_staff_service(self, service_list: List[MXService]) -> None:
        for staff_service in service_list:
            self.add_service(staff_service)

    def staff_dict(self):
        return {
            "nick_name": self._nick_name,
            "device_category": self._category.name,
            "vendor_id": self._vendor_id,
            "product_id": self._product_id,
            "uid": self._uid,
            "info": self._info,
        }

    @override
    def dict(self) -> dict:
        return super().dict() | {'manager_name': self._manager_name}

    @abstractmethod
    def setup_service_list(self) -> None:
        ...

    @abstractmethod
    async def setup(self) -> bool:
        ...

    @abstractmethod
    async def wrapup(self) -> bool:
        ...

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
    def uid(self) -> str:
        return self._uid

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @is_alive.setter
    def is_alive(self, is_alive: bool) -> None:
        self._is_alive = is_alive

    @uid.setter
    def uid(self, uid: str) -> None:
        self._uid = uid
