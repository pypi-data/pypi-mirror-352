from enum import Enum, auto
from typing import Union
import base64
import re
from typing_extensions import TypeAlias


IDENTIFIER_LIMIT = 256
STRING_VALUE_LIMIT = 100
STRING_ARG_VALUE_LIMIT = STRING_VALUE_LIMIT


class MXDeviceType(Enum):
    UNKNOWN = 0
    BLE = auto()
    BT = auto()
    NORMAL = auto()
    ZIGBEE = auto()
    MATTER = auto()
    REST_API = auto()
    LORA = auto()


class BinaryBase64:

    def __init__(self, text: str = None) -> None:
        self._data: bytes = None

        if text:
            self._data = base64.b64encode(text.encode())

    def __str__(self) -> str:
        return self._data.decode('utf-8')

    def __repr__(self) -> str:
        return self._data

    def __eq__(self, o: 'BinaryBase64') -> bool:
        if not isinstance(o, BinaryBase64):
            return False

        return self._data == o.data

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def text(self) -> str:
        return base64.b64decode(self._data).decode('utf-8')

    @classmethod
    def from_normal_string(cls, s: str) -> 'BinaryBase64':
        obj = cls.__new__(cls)
        obj._data = base64.b64encode(s.encode())
        return obj

    @classmethod
    def from_binary_string(cls, b: str) -> 'BinaryBase64':
        if cls.is_base64(b):
            obj = cls.__new__(cls)
            obj._data = b.encode()
            return obj
        else:
            raise ValueError('Input string is not a valid Base64 string.')

    @classmethod
    def from_file(cls, file_path: str) -> Union['BinaryBase64', None]:
        with open(file_path, 'rb') as f:
            encoded_string = base64.b64encode(f.read())
            instance = cls()
            instance._data = encoded_string
            return instance

    def to_file(self, file_path: str) -> None:
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(self._data))

    @staticmethod
    def is_base64(base64_str: str) -> bool:
        '''
        Checks if the given string is a Base64 encoded data URL according to RFC 2397.

        Format: data:[<mediatype>][;base64],<data>

        Args:
            base64_str: The data URL string to check.
        Returns:
            bool: True if the data URL is correctly Base64 encoded.
        '''
        if not base64_str.startswith('data:'):
            return False

        try:
            header, data = base64_str.split(',', 1)
            if ';base64' not in header:
                return False
            if len(data) <= STRING_VALUE_LIMIT or len(data) % 4 != 0:
                return False

            try:
                base64.b64decode(data, validate=True)
                return True
            except Exception:
                return False

        except Exception:
            return False


MXDataType: TypeAlias = Union[int, float, str, bool, BinaryBase64]


class MXType(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()

    UNDEFINED = auto()
    INTEGER = 'int'
    DOUBLE = 'double'
    STRING = 'string'
    BOOL = 'bool'
    BINARY = 'binary'
    ENUM = 'enum'
    LIST = 'list'
    DICT = 'dict'
    VOID = 'void'

    def __str__(self):
        return str(self.name)

    @classmethod
    def get(cls, name: Union[str, type]) -> 'MXType':
        try:
            if isinstance(name, str):
                name = name.lower()
                if name is not None:
                    for mxtype in MXType:
                        if mxtype.value == name:
                            return mxtype
                        elif mxtype.value == 'int' and name == 'integer':
                            return cls.INTEGER
                        elif mxtype.value == 'double' and name == 'float':
                            return cls.DOUBLE
                        elif mxtype.value == 'string' and name == 'str':
                            return cls.STRING
                        elif mxtype.value == 'binary' and name == 'binarybase64':
                            return cls.BINARY
                        elif mxtype.value == 'bool' and name == 'boolean':
                            return cls.BOOL
                    return cls.UNDEFINED
                else:
                    return cls.UNDEFINED
            elif isinstance(name, type):
                if name == int:
                    return MXType.INTEGER
                elif name == float:
                    return MXType.DOUBLE
                elif name == bool:
                    return MXType.BOOL
                elif name == str:
                    return MXType.STRING
                elif name == BinaryBase64:
                    return MXType.BINARY
                elif name in [None, type(None)]:
                    return MXType.VOID
            elif isinstance(name, BinaryBase64):
                return MXType.BINARY
            elif name is None:
                return cls.VOID
        except Exception:
            return cls.UNDEFINED

    def to_pytype(self):
        if self == MXType.INTEGER:
            return int
        elif self == MXType.DOUBLE:
            return float
        elif self == MXType.BOOL:
            return bool
        elif self == MXType.STRING:
            return str
        elif self == MXType.BINARY:
            return BinaryBase64
        elif self == MXType.VOID:
            return None


class MXActionType(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()

    REGISTER = auto()
    EXECUTE = auto()
    ALIVE = auto()
    VALUE_PUBLISH = auto()
    REFRESH = auto()
    SUPER_SCHEDULE = auto()
    SUPER_EXECUTE = auto()
    SUB_SCHEDULE = auto()
    SUB_EXECUTE = auto()
    INNER_EXECUTE = auto()


class MXProtocolType:
    class Base(Enum):
        # ===============
        # ___  ___ _____
        # |  \/  ||_   _|
        # | .  . |  | |
        # | |\/| |  | |
        # | |  | |  | |
        # \_|  |_/  \_/
        # ===============

        # MT/REQUEST_REGISTER_INFO/[ThingName]
        MT_REQUEST_REGISTER_INFO = 'MT/REQUEST_REGISTER_INFO/%s'

        # MT/REQUEST_UNREGISTER/[ThingName]
        MT_REQUEST_UNREGISTER = 'MT/REQUEST_UNREGISTER/%s'

        # MT/RESULT/REGISTER/[ThingName]
        MT_RESULT_REGISTER = 'MT/RESULT/REGISTER/%s'

        # MT/RESULT/UNREGISTER/[ThingName]
        MT_RESULT_UNREGISTER = 'MT/RESULT/UNREGISTER/%s'

        # MT/EXECUTE/[FunctionName]/[ThingName]/([TargetMiddlewareName]/[Request_ID])
        # Request_ID = requester_middleware@super_thing@super_service@target_thing
        MT_EXECUTE = 'MT/EXECUTE/%s/%s/%s/%s'

        # MT/IN/EXECUTE/[FunctionName]/[ThingName]
        MT_IN_EXECUTE = 'MT/IN/EXECUTE/%s/%s'

        # MT/RESULT/BINARY_VALUE/[ThingName]
        MT_RESULT_BINARY_VALUE = 'MT/RESULT/BINARY_VALUE/%s'

        # ===============
        #  _____ ___  ___
        # |_   _||  \/  |
        #   | |  | .  . |
        #   | |  | |\/| |
        #   | |  | |  | |
        #   \_/  \_|  |_/
        # ===============

        # TM/RESULT/EXECUTE/[FunctionName]/[ThingName]/([TargetMiddlewareName]/[Request_ID])
        # Request_ID = requester_middleware@super_thing@super_service@target_thing
        TM_RESULT_EXECUTE = 'TM/RESULT/EXECUTE/%s/%s/%s/%s'

        # TM/IN/RESULT/EXECUTE/[FunctionName]/[ThingName]
        TM_IN_RESULT_EXECUTE = 'TM/IN/RESULT/EXECUTE/%s/%s'

        # TM/REGISTER/[ThingName]
        TM_REGISTER = 'TM/REGISTER/%s'

        # TM/UNREGISTER/[ThingName]
        TM_UNREGISTER = 'TM/UNREGISTER/%s'

        # TM/ALIVE/[ThingName]
        TM_ALIVE = 'TM/ALIVE/%s'

        # [ValueName]/[ThingName]
        TM_VALUE_PUBLISH = '%s/%s'

        def get_prefix(self):
            topic_tree = self.value.split('/')
            result_topic = []
            for topic_part in topic_tree:
                if topic_part != '%s':
                    result_topic.append(topic_part)

            return '/'.join(result_topic)

    class Super(Enum):
        # ===============
        # ___  ___ _____
        # |  \/  |/  ___|
        # | .  . |\ `--.
        # | |\/| | `--. \
        # | |  | |/\__/ /
        # \_|  |_/\____/
        # ===============

        # MS/SCHEDULE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[RequesterMWName]
        MS_SCHEDULE = 'MS/SCHEDULE/%s/%s/%s/%s'

        # MS/EXECUTE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[RequesterMWName]
        MS_EXECUTE = 'MS/EXECUTE/%s/%s/%s/%s'

        # MS/RESULT/SCHEDULE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        # Request_ID = requester_middleware@super_thing@super_service@target_thing
        MS_RESULT_SCHEDULE = 'MS/RESULT/SCHEDULE/%s/SUPER/%s/%s'

        # MS/RESULT/EXECUTE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        # Request_ID = requester_middleware@super_thing@super_service@target_thing
        MS_RESULT_EXECUTE = 'MS/RESULT/EXECUTE/%s/SUPER/%s/%s'

        # MS/RESULT/SERVICE_LIST/[SuperThingName]
        MS_RESULT_SERVICE_LIST = 'MS/RESULT/SERVICE_LIST/%s'

        # ================
        #  _____ ___  ___
        # /  ___||  \/  |
        # \ `--. | .  . |
        #  `--. \| |\/| |
        # /\__/ /| |  | |
        # \____/ \_|  |_/
        # ================

        # SM/SCHEDULE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        # Request_ID = requester_middleware@super_thing@super_service@target_thing
        SM_SCHEDULE = 'SM/SCHEDULE/%s/SUPER/%s/%s'

        # SM/EXECUTE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        # Request_ID = requester_middleware@super_thing@super_service@target_thing
        SM_EXECUTE = 'SM/EXECUTE/%s/SUPER/%s/%s'

        # SM/RESULT/SCHEDULE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[RequesterMWName]
        SM_RESULT_SCHEDULE = 'SM/RESULT/SCHEDULE/%s/%s/%s/%s'

        # SM/RESULT/EXECUTE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[RequesterMWName]
        SM_RESULT_EXECUTE = 'SM/RESULT/EXECUTE/%s/%s/%s/%s'

        # SM/REFRESH/[SuperThingName]
        SM_REFRESH = 'SM/REFRESH/%s'

        # ==================
        #   _____    _____
        #  |  __ \  / ____|
        #  | |__) || |
        #  |  ___/ | |
        #  | |     | |____
        #  |_|      \_____|
        # ==================

        # PC/SCHEDULE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        PC_SCHEDULE = 'PC/SCHEDULE/%s/SUPER/%s/%s'

        # PC/EXECUTE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        PC_EXECUTE = 'PC/EXECUTE/%s/SUPER/%s/%s'

        # PC/RESULT/SCHEDULE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[RequesterMWName]
        PC_RESULT_SCHEDULE = 'PC/RESULT/SCHEDULE/%s/%s/%s/%s'

        # PC/RESULT/EXECUTE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[RequesterMWName]
        PC_RESULT_EXECUTE = 'PC/RESULT/EXECUTE/%s/%s/%s/%s'

        # PC/SERVICE_LIST/#
        PC_SERVICE_LIST = 'PC/SERVICE_LIST/%s'

        # ==================
        #    _____  _____
        #   / ____||  __ \
        #  | |     | |__) |
        #  | |     |  ___/
        #  | |____ | |
        #   \_____||_|
        # ==================

        # CP/SCHEDULE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[RequesterMWName]
        CP_SCHEDULE = 'CP/SCHEDULE/%s/%s/%s/%s'

        # CP/EXECUTE/[SuperFunctionName]/[SuperThingName]/[SuperMiddlewareName]/[Requester MWName]
        CP_EXECUTE = 'CP/EXECUTE/%s/%s/%s/%s'

        # CP/RESULT/SCHEDULE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        CP_RESULT_SCHEDULE = 'CP/RESULT/SCHEDULE/%s/SUPER/%s/%s'

        # CP/RESULT/EXECUTE/[TargetFunctionName]/SUPER/[TargetMiddlewareName]/[Request_ID]
        CP_RESULT_EXECUTE = 'CP/RESULT/EXECUTE/%s/SUPER/%s/%s'

        # CP/SERVICE_LIST/#
        CP_SERVICE_LIST = 'CP/SERVICE_LIST/%s'

        def get_prefix(self):
            topic_tree = self.value.split('/')
            result_topic = []
            for topic_part in topic_tree:
                if topic_part != '%s':
                    result_topic.append(topic_part)

            return '/'.join(result_topic)

    class WebClient(Enum):
        # ==================
        #   ______  __  __
        #  |  ____||  \/  |
        #  | |__   | \  / |
        #  |  __|  | |\/| |
        #  | |____ | |  | |
        #  |______||_|  |_|
        # ==================

        # Hub Connect
        # EM/REQUEST_CONNECTION/[ClientID]
        EM_REQUEST_CONNECTION = 'EM/REQUEST_CONNECTION/%s'

        # EM/CONNECT_AS_OWNER/[ClientID]
        EM_CONNECT_AS_OWNER = 'EM/CONNECT_AS_OWNER/%s'

        # Member Manage
        # EM/SET_MEMBER_LEVEL/[ClientID]
        EM_SET_MEMBER_LEVEL = 'EM/SET_MEMBER_LEVEL/%s'

        # EM/SET_MEMBER_STATE/[ClientID]
        EM_SET_MEMBER_STATE = 'EM/SET_MEMBER_STATE/%s'

        # EM/DELETE_MEMBER/[ClientID]
        EM_DELETE_MEMBER = 'EM/DELETE_MEMBER/%s'

        # EM/ADD_THING_FAVORITE/[ClientID]
        EM_ADD_THING_FAVORITE = 'EM/ADD_THING_FAVORITE/%s'

        # EM/DELETE_THING_FAVORITE/[ClientID]
        EM_DELETE_THING_FAVORITE = 'EM/DELETE_THING_FAVORITE/%s'

        # EM/ADD_SERVICE_FAVORITE/[ClientID]
        EM_ADD_SERVICE_FAVORITE = 'EM/ADD_SERVICE_FAVORITE/%s'

        # EM/DELETE_SERVICE_FAVORITE/[ClientID]
        EM_DELETE_SERVICE_FAVORITE = 'EM/DELETE_SERVICE_FAVORITE/%s'

        # EM/ADD_SCENARIO_FAVORITE/[ClientID]
        EM_ADD_SCENARIO_FAVORITE = 'EM/ADD_SCENARIO_FAVORITE/%s'

        # EM/DELETE_SCENARIO_FAVORITE/[ClientID]
        EM_DELETE_SCENARIO_FAVORITE = 'EM/DELETE_SCENARIO_FAVORITE/%s'

        # Device Manage
        # EM/REGISTER_THING/[ClientID]
        EM_REGISTER_THING = 'EM/REGISTER_THING/%s'

        # EM/UNREGISTER_THING/[ClientID]
        EM_UNREGISTER_THING = 'EM/UNREGISTER_THING/%s'

        # EM/SET_NICK_NAME/[ClientID]
        EM_SET_NICK_NAME = 'EM/SET_NICK_NAME/%s'

        # EM/SET_DESCRIPTION/[ClientID]
        EM_SET_DESCRIPTION = 'EM/SET_DESCRIPTION/%s'

        # EM/REQUEST_SCAN/[ClientID]
        EM_REQUEST_SCAN = 'EM/REQUEST_SCAN/%s'

        # EM/OPEN_WINDOW_MATTER/[ClientID]
        EM_OPEN_WINDOW_MATTER = 'EM/OPEN_WINDOW_MATTER/%s'

        # EM/CLOSE_WINDOW_MATTER/[ClientID]
        EM_CLOSE_WINDOW_MATTER = 'EM/CLOSE_WINDOW_MATTER/%s'

        # Scenario Manage
        # EM/VERIFY_SCENARIO/[ClientID]
        EM_VERIFY_SCENARIO = 'EM/VERIFY_SCENARIO/%s'

        # EM/ADD_SCENARIO/[ClientID]
        EM_ADD_SCENARIO = 'EM/ADD_SCENARIO/%s'

        # EM/RUN_SCENARIO/[ClientID]
        EM_RUN_SCENARIO = 'EM/RUN_SCENARIO/%s'

        # EM/STOP_SCENARIO/[ClientID]
        EM_STOP_SCENARIO = 'EM/STOP_SCENARIO/%s'

        # EM/UPDATE_SCENARIO/[ClientID]
        EM_UPDATE_SCENARIO = 'EM/UPDATE_SCENARIO/%s'

        # EM/MODIFY_SCENARIO/[ClientID]
        EM_MODIFY_SCENARIO = 'EM/MODIFY_SCENARIO/%s'

        # EM/DELETE_SCENARIO/[ClientID]
        EM_DELETE_SCENARIO = 'EM/DELETE_SCENARIO/%s'

        # Service Manage
        # EM/ADD_TAG/[ClientID]
        EM_ADD_TAG = 'EM/ADD_TAG/%s'

        # EM/DELETE_TAG/[ClientID]
        EM_DELETE_TAG = 'EM/DELETE_TAG/%s'

        # EM/SET_ACCESS/[ClientID]
        EM_SET_ACCESS = 'EM/SET_ACCESS/%s'

        # EM/SET_OPENED/[ClientID]
        EM_SET_OPENED = 'EM/SET_OPENED/%s'

        # EM/INSTANT_EXECUTE/[ClientID]
        EM_INSTANT_EXECUTE = 'EM/INSTANT_EXECUTE/%s'

        # Sync Info
        # EM/REFRESH/[ClientID]
        EM_REFRESH = 'EM/REFRESH/%s'

        # EM/GET_THING/[ClientID]
        EM_GET_THING = 'EM/GET_THING/%s'

        # EM/GET_SERVICE/[ClientID]
        EM_GET_SERVICE = 'EM/GET_SERVICE/%s'

        # EM/GET_SCENARIO/[ClientID]
        EM_GET_SCENARIO = 'EM/GET_SCENARIO/%s'

        # EM/GET_MEMBER/[ClientID]
        EM_GET_MEMBER = 'EM/GET_MEMBER/%s'

        # EM/GET_THING_LIST/[ClientID]
        EM_GET_THING_LIST = 'EM/GET_THING_LIST/%s'

        # EM/GET_SERVICE_LIST/[ClientID]
        EM_GET_SERVICE_LIST = 'EM/GET_SERVICE_LIST/%s'

        # EM/GET_SCENARIO_LIST/[ClientID]
        EM_GET_SCENARIO_LIST = 'EM/GET_SCENARIO_LIST/%s'

        # EM/GET_MEMBER_LIST/[ClientID]
        EM_GET_MEMBER_LIST = 'EM/GET_MEMBER_LIST/%s'

        # EM/SET_LOCATION/[ClientID]
        EM_SET_LOCATION = 'EM/SET_LOCATION/%s'

        # EM/GET_LOCATION/[ClientID]
        EM_GET_LOCATION = 'EM/GET_LOCATION/%s'

        # EM/GET_HOME/[ClientID]
        EM_GET_HOME = 'EM/GET_HOME/%s'

        # EM/GET_FAVORITES/[ClientID]
        EM_GET_FAVORITES = 'EM/GET_FAVORITES/%s'

        # Hub Reset
        # EM/RESET_HUB/[ClientID]
        EM_RESET_HUB = 'EM/RESET_HUB/%s'

        # ==================
        #   __  __  ______
        #  |  \/  ||  ____|
        #  | \  / || |__
        #  | |\/| ||  __|
        #  | |  | || |____
        #  |_|  |_||______|
        # ==================

        # Hub Connect
        # ME/RESULT/REQUEST_CONNECTION/[ClientID]
        ME_RESULT_REQUEST_CONNECTION = 'ME/RESULT/REQUEST_CONNECTION/%s'

        # ME/OWNER_BUTTON_CLICKED
        ME_OWNER_BUTTON_CLICKED = 'ME/OWNER_BUTTON_CLICKED'

        # ME/RESULT/CONNECT_AS_OWNER/[ClientID]
        ME_RESULT_CONNECT_AS_OWNER = 'ME/RESULT/CONNECT_AS_OWNER/%s'

        # Member Manage
        # ME/RESULT/SET_MEMBER_LEVEL/[ClientID]
        ME_RESULT_SET_MEMBER_LEVEL = 'ME/RESULT/SET_MEMBER_LEVEL/%s'

        # ME/RESULT/SET_MEMBER_STATE/[ClientID]
        ME_RESULT_SET_MEMBER_STATE = 'ME/RESULT/SET_MEMBER_STATE/%s'

        # ME/RESULT/DELETE_MEMBER/[ClientID]
        ME_RESULT_DELETE_MEMBER = 'ME/RESULT/DELETE_MEMBER/%s'

        # ME/RESULT/ADD_THING_FAVORITE/[ClientID]
        ME_RESULT_ADD_THING_FAVORITE = 'ME/RESULT/ADD_THING_FAVORITE/%s'

        # ME/RESULT/DELETE_THING_FAVORITE/[ClientID]
        ME_RESULT_DELETE_THING_FAVORITE = 'ME/RESULT/DELETE_THING_FAVORITE/%s'

        # ME/RESULT/ADD_SERVICE_FAVORITE/[ClientID]
        ME_RESULT_ADD_SERVICE_FAVORITE = 'ME/RESULT/ADD_SERVICE_FAVORITE/%s'

        # ME/RESULT/DELETE_SERVICE_FAVORITE/[ClientID]
        ME_RESULT_DELETE_SERVICE_FAVORITE = 'ME/RESULT/DELETE_SERVICE_FAVORITE/%s'

        # ME/RESULT/ADD_SCENARIO_FAVORITE/[ClientID]
        ME_RESULT_ADD_SCENARIO_FAVORITE = 'ME/RESULT/ADD_SCENARIO_FAVORITE/%s'

        # ME/RESULT/DELETE_SCENARIO_FAVORITE/[ClientID]
        ME_RESULT_DELETE_SCENARIO_FAVORITE = 'ME/RESULT/DELETE_SCENARIO_FAVORITE/%s'

        # Device Manage
        # ME/RESULT/REGISTER_THING/[ClientID]
        ME_RESULT_REGISTER_THING = 'ME/RESULT/REGISTER_THING/%s'

        # ME/RESULT/UNREGISTER/[ClientID]
        ME_RESULT_UNREGISTER_THING = 'ME/RESULT/UNREGISTER_THING/%s'

        # ME/RESULT/SET_NICK_NAME/[ClientID]
        ME_RESULT_SET_NICK_NAME = 'ME/RESULT/SET_NICK_NAME/%s'

        # ME/RESULT/SET_DESCRIPTION/[ClientID]
        ME_RESULT_SET_DESCRIPTION = 'ME/RESULT/SET_DESCRIPTION/%s'

        # ME/SCAN_RESULT/[ClientID]
        ME_SCAN_RESULT = 'ME/SCAN_RESULT/%s'

        # ME/RESULT/OPEN_WINDOW_MATTER/[ClientID]
        ME_RESULT_OPEN_WINDOW_MATTER = 'ME/RESULT/OPEN_WINDOW_MATTER/%s'

        # ME/RESULT/CLOSE_WINDOW_MATTER/[ClientID]
        ME_RESULT_CLOSE_WINDOW_MATTER = 'ME/RESULT/CLOSE_WINDOW_MATTER/%s'

        # Scenario Manage
        # ME/RESULT/VERIFY_SCENARIO/[ClientID]
        ME_RESULT_VERIFY_SCENARIO = 'ME/RESULT/VERIFY_SCENARIO/%s'

        # ME/RESULT/RUN_SCENARIO/[ClientID]
        ME_RESULT_RUN_SCENARIO = 'ME/RESULT/RUN_SCENARIO/%s'

        # ME/RESULT/STOP_SCENARIO/[ClientID]
        ME_RESULT_STOP_SCENARIO = 'ME/RESULT/STOP_SCENARIO/%s'

        # ME/RESULT/SCHEDULE_SCENARIO/[ClientID]
        ME_RESULT_SCHEDULE_SCENARIO = 'ME/RESULT/SCHEDULE_SCENARIO/%s'

        # ME/RESULT/SCHEDULE_SCENARIO/[ClientID]
        ME_RESULT_ADD_SCENARIO = ME_RESULT_SCHEDULE_SCENARIO

        # ME/RESULT/SCHEDULE_SCENARIO/[ClientID]
        ME_RESULT_UPDATE_SCENARIO = ME_RESULT_SCHEDULE_SCENARIO

        # ME/RESULT/SCHEDULE_SCENARIO/[ClientID]
        ME_RESULT_MODIFY_SCENARIO = ME_RESULT_SCHEDULE_SCENARIO

        # ME/RESULT/DELETE_SCENARIO/[ClientID]
        ME_RESULT_DELETE_SCENARIO = 'ME/RESULT/DELETE_SCENARIO/%s'

        # Service Manage
        # ME/RESULT/ADD_TAG/[ClientID]
        ME_RESULT_ADD_TAG = 'ME/RESULT/ADD_TAG/%s'

        # ME/RESULT/DELETE_TAG/[ClientID]
        ME_RESULT_DELETE_TAG = 'ME/RESULT/DELETE_TAG/%s'

        # ME/RESULT/SET_ACCESS/[ClientID]
        ME_RESULT_SET_ACCESS = 'ME/RESULT/SET_ACCESS/%s'

        # ME/RESULT/SET_OPENED/[ClientID]
        ME_RESULT_SET_OPENED = 'ME/RESULT/SET_OPENED/%s'

        # ME/RESULT/INSTANT_EXECUTE/[ExecID]
        ME_RESULT_INSTANT_EXECUTE = 'ME/RESULT/INSTANT_EXECUTE/%s'

        # Sync Info
        # ME/RESULT/THING/[ClientID]
        ME_RESULT_THING = 'ME/RESULT/THING/%s'

        # ME/RESULT/SERVICE/[ClientID]
        ME_RESULT_SERVICE = 'ME/RESULT/SERVICE/%s'

        # ME/RESULT/SCENARIO/[ClientID]
        ME_RESULT_SCENARIO = 'ME/RESULT/SCENARIO/%s'

        # ME/RESULT/MEMBER/[ClientID]
        ME_RESULT_MEMBER = 'ME/RESULT/MEMBER/%s'

        # ME/RESULT/THING_LIST/[ClientID]
        ME_RESULT_THING_LIST = 'ME/RESULT/THING_LIST/%s'

        # ME/RESULT/SERVICE_LIST/[ClientID]
        ME_RESULT_SERVICE_LIST = 'ME/RESULT/SERVICE_LIST/%s'

        # ME/RESULT/SCENARIO_LIST/[ClientID]
        ME_RESULT_SCENARIO_LIST = 'ME/RESULT/SCENARIO_LIST/%s'

        # ME/RESULT/MEMBER_LIST/[ClientID]
        ME_RESULT_MEMBER_LIST = 'ME/RESULT/MEMBER_LIST/%s'

        # ME/RESULT/SET_LOCATION/[ClientID]
        ME_RESULT_SET_LOCATION = 'ME/RESULT/SET_LOCATION/%s'

        # ME/RESULT/GET_LOCATION/[ClientID]
        ME_RESULT_GET_LOCATION = 'ME/RESULT/GET_LOCATION/%s'

        # ME/RESULT/HOME/[ClientID]
        ME_RESULT_HOME = 'ME/RESULT/HOME/%s'

        # ME/RESULT/GET_FAVORITES/[ClientID]
        ME_RESULT_GET_FAVORITES = 'ME/RESULT/GET_FAVORITES/%s'

        # Notify
        # ME/NOTIFY_MESSAGE/[ClientID]
        ME_NOTIFY_MESSAGE = 'ME/NOTIFY_MESSAGE/%s'

        # ME/NOTIFY_CHANGE/[ClientID]
        ME_NOTIFY_CHANGE = 'ME/NOTIFY_CHANGE/%s'

        # Hub Reset
        # ME/RESULT/RESET_HUB/[ClientID]
        ME_RESULT_RESET_HUB = 'ME/RESULT/RESET_HUB/%s'

        def get_prefix(self):
            topic_tree = self.value.split('/')
            result_topic = []
            for topic_part in topic_tree:
                if topic_part != '%s':
                    result_topic.append(topic_part)

            return '/'.join(result_topic)

    class SN(Enum):
        # TM/SN/REGISTER/VALUE/[Thing ID]
        TM_SN_REGISTER_VALUE = "TM/SN/REGISTER/VALUE/%s"

        # TM/SN/REGISTER/VALUEDESC/[Thing ID]
        TM_SN_REGISTER_VALUEDESC = "TM/SN/REGISTER/VALUEDESC/%s"

        # TM/SN/REGISTER/VALUETAG/[Thing ID]
        TM_SN_REGISTER_VALUETAG = "TM/SN/REGISTER/VALUETAG/%s"

        # TM/SN/REGISTER/FUNCTION/[Thing ID]
        TM_SN_REGISTER_FUNCTION = "TM/SN/REGISTER/FUNCTION/%s"

        # TM/SN/REGISTER/FUNCTIONDESC/[Thing ID]
        TM_SN_REGISTER_FUNCTIONDESC = "TM/SN/REGISTER/FUNCTIONDESC/%s"

        # TM/SN/REGISTER/FUNCTIONTAG/[Thing ID]
        TM_SN_REGISTER_FUNCTIONTAG = "TM/SN/REGISTER/FUNCTIONTAG/%s"

        # TM/SN/REGISTER/ARGUMENT/[Thing ID]
        TM_SN_REGISTER_ARGUMENT = "TM/SN/REGISTER/ARGUMENT/%s"

        # TM/SN/REGISTER/ALIVECYCLE/[Thing ID]
        TM_SN_REGISTER_ALIVECYCLE = "TM/SN/REGISTER/ALIVECYCLE/%s"

        # TM/SN/REGISTER/FINISH/[Thing ID]
        TM_SN_REGISTER_FINISH = "TM/SN/REGISTER/FINISH/%s"

        def get_prefix(self):
            topic_tree = self.value.split('/')
            result_topic = []
            for topic_part in topic_tree:
                if topic_part != '%s':
                    result_topic.append(topic_part)

            return '/'.join(result_topic)

    @classmethod
    def get(cls, topic: str) -> 'MXProtocolType':
        # MT
        if 'MT/REQUEST_REGISTER_INFO/' in topic:
            return cls.Base.MT_REQUEST_REGISTER_INFO
        elif 'MT/REQUEST_UNREGISTER/' in topic:
            return cls.Base.MT_REQUEST_UNREGISTER
        elif 'MT/RESULT/REGISTER/' in topic:
            return cls.Base.MT_RESULT_REGISTER
        elif 'MT/RESULT/UNREGISTER/' in topic:
            return cls.Base.MT_RESULT_UNREGISTER
        elif 'MT/EXECUTE/' in topic:
            return cls.Base.MT_EXECUTE
        elif 'MT/IN/EXECUTE/' in topic:
            return cls.Base.MT_IN_EXECUTE
        elif 'MT/RESULT/BINARY_VALUE/' in topic:
            return cls.Base.MT_RESULT_BINARY_VALUE
        # TM
        elif 'TM/RESULT/EXECUTE/' in topic:
            return cls.Base.TM_RESULT_EXECUTE
        elif 'TM/IN/RESULT/EXECUTE/' in topic:
            return cls.Base.TM_IN_RESULT_EXECUTE
        elif 'TM/REGISTER/' in topic:
            return cls.Base.TM_REGISTER
        elif 'TM/UNREGISTER/' in topic:
            return cls.Base.TM_UNREGISTER
        elif 'TM/ALIVE/' in topic:
            return cls.Base.TM_ALIVE
        elif len(topic.split('/')) == 2:
            return cls.Base.TM_VALUE_PUBLISH
        # MS
        elif 'MS/SCHEDULE/' in topic:
            return cls.Super.MS_SCHEDULE
        elif 'MS/EXECUTE/' in topic:
            return cls.Super.MS_EXECUTE
        elif 'MS/RESULT/SCHEDULE/' in topic:
            return cls.Super.MS_RESULT_SCHEDULE
        elif 'MS/RESULT/EXECUTE/' in topic:
            return cls.Super.MS_RESULT_EXECUTE
        elif 'MS/RESULT/SERVICE_LIST/' in topic:
            return cls.Super.MS_RESULT_SERVICE_LIST
        # SM
        elif 'SM/SCHEDULE/' in topic:
            return cls.Super.SM_SCHEDULE
        elif 'SM/EXECUTE/' in topic:
            return cls.Super.SM_EXECUTE
        elif 'SM/RESULT/SCHEDULE/' in topic:
            return cls.Super.SM_RESULT_SCHEDULE
        elif 'SM/RESULT/EXECUTE/' in topic:
            return cls.Super.SM_RESULT_EXECUTE
        elif 'SM/REFRESH/' in topic:
            return cls.Super.SM_REFRESH
        # PC
        elif 'PC/SCHEDULE/' in topic:
            return cls.Super.PC_SCHEDULE
        elif 'PC/EXECUTE/' in topic:
            return cls.Super.PC_EXECUTE
        elif 'PC/RESULT/SCHEDULE/' in topic:
            return cls.Super.PC_RESULT_SCHEDULE
        elif 'PC/RESULT/EXECUTE/' in topic:
            return cls.Super.PC_RESULT_EXECUTE
        elif 'PC/SERVICE_LIST/' in topic:
            return cls.Super.PC_SERVICE_LIST
        # CP
        elif 'CP/SCHEDULE/' in topic:
            return cls.Super.CP_SCHEDULE
        elif 'CP/EXECUTE/' in topic:
            return cls.Super.CP_EXECUTE
        elif 'CP/RESULT/SCHEDULE/' in topic:
            return cls.Super.CP_RESULT_SCHEDULE
        elif 'CP/RESULT/EXECUTE/' in topic:
            return cls.Super.CP_RESULT_EXECUTE
        elif 'CP/SERVICE_LIST/' in topic:
            return cls.Super.CP_SERVICE_LIST
        # EM
        if 'EM/REQUEST_CONNECTION/' in topic:
            return cls.WebClient.EM_REQUEST_CONNECTION
        elif 'EM/CONNECT_AS_OWNER/' in topic:
            return cls.WebClient.EM_CONNECT_AS_OWNER
        elif 'EM/SET_MEMBER_LEVEL/' in topic:
            return cls.WebClient.EM_SET_MEMBER_LEVEL
        elif 'EM/SET_MEMBER_STATE/' in topic:
            return cls.WebClient.EM_SET_MEMBER_STATE
        elif 'EM/DELETE_MEMBER/' in topic:
            return cls.WebClient.EM_DELETE_MEMBER
        elif 'EM/ADD_THING_FAVORITE/' in topic:
            return cls.WebClient.EM_ADD_THING_FAVORITE
        elif 'EM/DELETE_THING_FAVORITE/' in topic:
            return cls.WebClient.EM_DELETE_THING_FAVORITE
        elif 'EM/ADD_SERVICE_FAVORITE/' in topic:
            return cls.WebClient.EM_ADD_SERVICE_FAVORITE
        elif 'EM/DELETE_SERVICE_FAVORITE/' in topic:
            return cls.WebClient.EM_DELETE_SERVICE_FAVORITE
        elif 'EM/ADD_SCENARIO_FAVORITE/' in topic:
            return cls.WebClient.EM_ADD_SCENARIO_FAVORITE
        elif 'EM/DELETE_SCENARIO_FAVORITE/' in topic:
            return cls.WebClient.EM_DELETE_SCENARIO_FAVORITE
        elif 'EM/REGISTER_THING/' in topic:
            return cls.WebClient.EM_REGISTER_THING
        elif 'EM/UNREGISTER_THING/' in topic:
            return cls.WebClient.EM_UNREGISTER_THING
        elif 'EM/SET_NICK_NAME/' in topic:
            return cls.WebClient.EM_SET_NICK_NAME
        elif 'EM/SET_DESCRIPTION/' in topic:
            return cls.WebClient.EM_SET_DESCRIPTION
        elif 'EM/REQUEST_SCAN/' in topic:
            return cls.WebClient.EM_REQUEST_SCAN
        elif 'EM/OPEN_WINDOW_MATTER/' in topic:
            return cls.WebClient.EM_OPEN_WINDOW_MATTER
        elif 'EM/CLOSE_WINDOW_MATTER/' in topic:
            return cls.WebClient.EM_CLOSE_WINDOW_MATTER
        elif 'EM/EXECUTE/' in topic:
            return cls.WebClient.EM_INSTANT_EXECUTE
        elif 'EM/SET_ACCESS/' in topic:
            return cls.WebClient.EM_SET_ACCESS
        elif 'EM/SET_OPENED/' in topic:
            return cls.WebClient.EM_SET_OPENED
        elif 'EM/REFRESH/' in topic:
            return cls.WebClient.EM_REFRESH
        elif 'EM/GET_THING/' in topic:
            return cls.WebClient.EM_GET_THING
        elif 'EM/GET_SERVICE/' in topic:
            return cls.WebClient.EM_GET_SERVICE
        elif 'EM/GET_SCENARIO/' in topic:
            return cls.WebClient.EM_GET_SCENARIO
        elif 'EM/GET_MEMBER/' in topic:
            return cls.WebClient.EM_GET_MEMBER
        elif 'EM/GET_THING_LIST/' in topic:
            return cls.WebClient.EM_GET_THING_LIST
        elif 'EM/GET_SERVICE_LIST/' in topic:
            return cls.WebClient.EM_GET_SERVICE_LIST
        elif 'EM/GET_SCENARIO_LIST/' in topic:
            return cls.WebClient.EM_GET_SCENARIO_LIST
        elif 'EM/GET_MEMBER_LIST/' in topic:
            return cls.WebClient.EM_GET_MEMBER_LIST
        elif 'EM/SET_LOCATION/' in topic:
            return cls.WebClient.EM_SET_LOCATION
        elif 'EM/GET_LOCATION/' in topic:
            return cls.WebClient.EM_GET_LOCATION
        elif 'EM/GET_HOME/' in topic:
            return cls.WebClient.EM_GET_HOME
        elif 'EM/GET_FAVORITES/' in topic:
            return cls.WebClient.EM_GET_FAVORITES
        elif 'EM/RESET_HUB/' in topic:
            return cls.WebClient.EM_RESET_HUB
        # ME
        elif 'ME/RESULT/REQUEST_CONNECTION/' in topic:
            return cls.WebClient.ME_RESULT_REQUEST_CONNECTION
        elif 'ME/OWNER_BUTTON_CLICKED' in topic:
            return cls.WebClient.ME_OWNER_BUTTON_CLICKED
        elif 'ME/RESULT/CONNECT_AS_OWNER/' in topic:
            return cls.WebClient.ME_RESULT_CONNECT_AS_OWNER
        elif 'ME/RESULT/SET_MEMBER_LEVEL/' in topic:
            return cls.WebClient.ME_RESULT_SET_MEMBER_LEVEL
        elif 'ME/RESULT/SET_MEMBER_STATE/' in topic:
            return cls.WebClient.ME_RESULT_SET_MEMBER_STATE
        elif 'ME/RESULT/DELETE_MEMBER/' in topic:
            return cls.WebClient.ME_RESULT_DELETE_MEMBER
        elif 'ME/RESULT/ADD_THING_FAVORITE/' in topic:
            return cls.WebClient.ME_RESULT_ADD_THING_FAVORITE
        elif 'ME/RESULT/DELETE_THING_FAVORITE/' in topic:
            return cls.WebClient.ME_RESULT_DELETE_THING_FAVORITE
        elif 'ME/RESULT/ADD_SERVICE_FAVORITE/' in topic:
            return cls.WebClient.ME_RESULT_ADD_SERVICE_FAVORITE
        elif 'ME/RESULT/DELETE_SERVICE_FAVORITE/' in topic:
            return cls.WebClient.ME_RESULT_DELETE_SERVICE_FAVORITE
        elif 'ME/RESULT/ADD_SCENARIO_FAVORITE/' in topic:
            return cls.WebClient.ME_RESULT_ADD_SCENARIO_FAVORITE
        elif 'ME/RESULT/DELETE_SCENARIO_FAVORITE/' in topic:
            return cls.WebClient.ME_RESULT_DELETE_SCENARIO_FAVORITE
        elif 'ME/RESULT/REGISTER_THING/' in topic:
            return cls.WebClient.ME_RESULT_REGISTER_THING
        elif 'ME/RESULT/UNREGISTER_THING/' in topic:
            return cls.WebClient.ME_RESULT_UNREGISTER_THING
        elif 'ME/RESULT/SET_NICK_NAME/' in topic:
            return cls.WebClient.ME_RESULT_SET_NICK_NAME
        elif 'ME/RESULT/SET_DESCRIPTION/' in topic:
            return cls.WebClient.ME_RESULT_SET_DESCRIPTION
        elif 'ME/SCAN_RESULT/' in topic:
            return cls.WebClient.ME_SCAN_RESULT
        elif 'ME/RESULT/OPEN_WINDOW_MATTER/' in topic:
            return cls.WebClient.ME_RESULT_OPEN_WINDOW_MATTER
        elif 'ME/RESULT/CLOSE_WINDOW_MATTER/' in topic:
            return cls.WebClient.ME_RESULT_CLOSE_WINDOW_MATTER
        elif 'ME/RESULT/SET_ACCESS/' in topic:
            return cls.WebClient.ME_RESULT_SET_ACCESS
        elif 'ME/RESULT/SET_OPENED/' in topic:
            return cls.WebClient.ME_RESULT_SET_OPENED
        elif 'ME/RESULT/THING/' in topic:
            return cls.WebClient.ME_RESULT_THING
        elif 'ME/RESULT/SERVICE/' in topic:
            return cls.WebClient.ME_RESULT_SERVICE
        elif 'ME/RESULT/SCENARIO/' in topic:
            return cls.WebClient.ME_RESULT_SCENARIO
        elif 'ME/RESULT/MEMBER/' in topic:
            return cls.WebClient.ME_RESULT_MEMBER
        elif 'ME/RESULT/THING_LIST/' in topic:
            return cls.WebClient.ME_RESULT_THING_LIST
        elif 'ME/RESULT/SERVICE_LIST/' in topic:
            return cls.WebClient.ME_RESULT_SERVICE_LIST
        elif 'ME/RESULT/SCENARIO_LIST/' in topic:
            return cls.WebClient.ME_RESULT_SCENARIO_LIST
        elif 'ME/RESULT/MEMBER_LIST/' in topic:
            return cls.WebClient.ME_RESULT_MEMBER_LIST
        elif 'ME/RESULT/SET_LOCATION/' in topic:
            return cls.WebClient.ME_RESULT_SET_LOCATION
        elif 'ME/RESULT/GET_LOCATION/' in topic:
            return cls.WebClient.ME_RESULT_GET_LOCATION
        elif 'ME/RESULT/HOME/' in topic:
            return cls.WebClient.ME_RESULT_HOME
        elif 'ME/RESULT/GET_FAVORITES/' in topic:
            return cls.WebClient.ME_RESULT_GET_FAVORITES
        elif 'ME/NOTIFY_MESSAGE/' in topic:
            return cls.WebClient.ME_NOTIFY_MESSAGE
        elif 'ME/RESULT/RESET_HUB/' in topic:
            return cls.WebClient.ME_RESULT_RESET_HUB
        # TM/SN
        elif 'TM/SN/REGISTER/VALUE/' in topic:
            return cls.SN.TM_SN_REGISTER_VALUE
        elif 'TM/SN/REGISTER/VALUEDESC/' in topic:
            return cls.SN.TM_SN_REGISTER_VALUEDESC
        elif 'TM/SN/REGISTER/VALUETAG/' in topic:
            return cls.SN.TM_SN_REGISTER_VALUETAG
        elif 'TM/SN/REGISTER/FUNCTION/' in topic:
            return cls.SN.TM_SN_REGISTER_FUNCTION
        elif 'TM/SN/REGISTER/FUNCTIONDESC/' in topic:
            return cls.SN.TM_SN_REGISTER_FUNCTIONDESC
        elif 'TM/SN/REGISTER/FUNCTIONTAG/' in topic:
            return cls.SN.TM_SN_REGISTER_FUNCTIONTAG
        elif 'TM/SN/REGISTER/ARGUMENT/' in topic:
            return cls.SN.TM_SN_REGISTER_ARGUMENT
        elif 'TM/SN/REGISTER/ALIVECYCLE/' in topic:
            return cls.SN.TM_SN_REGISTER_ALIVECYCLE
        elif 'TM/SN/REGISTER/FINISH/' in topic:
            return cls.SN.TM_SN_REGISTER_FINISH
        else:
            return None


class MXRangeType(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()

    UNDEFINED = auto()
    ALL = auto()
    SINGLE = auto()

    @classmethod
    def get(cls, name: str) -> 'MXRangeType':
        try:
            return cls[name.upper()]
        except Exception:
            return cls.UNDEFINED


class HierarchyType(Enum):
    LOCAL = 0
    PARENT = 1
    CHILD = 2


class MXServiceType(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()

    UNDEFINED = auto()
    VALUE = auto()
    FUNCTION = auto()

    @classmethod
    def get(cls, name: str) -> 'MXServiceType':
        try:
            return cls[name.upper()]
        except Exception:
            return cls.UNDEFINED


if __name__ == '__main__':
    a = BinaryBase64('this is normal string')
    b = BinaryBase64.from_normal_string('this is normal string')
    c = BinaryBase64.from_binary_string('dGhpcyBpcyBub3JtYWwgc3RyaW5n')
    d = BinaryBase64.from_file(__file__)

    print(f'normal string:\n{a.text}\n binary string:\n{a.data}')
    print(f'normal string:\n{b.text}\n binary string:\n{b.data}')
    print(f'normal string:\n{c.text}\n binary string:\n{c.data}')
    print(f'normal string:\n{d.text}\n binary string:\n{d.data}')
