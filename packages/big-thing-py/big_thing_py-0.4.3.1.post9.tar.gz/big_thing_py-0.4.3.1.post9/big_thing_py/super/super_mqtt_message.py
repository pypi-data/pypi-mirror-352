from big_thing_py.utils import *
from big_thing_py.core.mqtt_message import *
from ..super.helper.util import *


class MXSchedulePhase(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()

    UNDEFINED = auto()
    CHECK = auto()
    CONFIRM = auto()

    @classmethod
    def get(cls, name: str) -> 'MXScheduleStatus':
        try:
            return cls[name.upper()]
        except Exception:
            return cls.UNDEFINED


class MXScheduleStatus(Enum):
    def _generate_next_value_(name: str, start, count, last_values):
        return name.lower()

    UNDEFINED = auto()
    INIT = auto()
    CHECK_PENDING = auto()
    CHECKED = auto()
    CONFIRM_PENDING = auto()
    CONFIRMED = auto()

    @classmethod
    def get(cls, name: str) -> 'MXScheduleStatus':
        try:
            return cls[name.upper()]
        except Exception:
            return cls.UNDEFINED


class MXSuperRefreshMessage(MXMQTTSendMessage):

    def __init__(self, thing_name: str) -> None:
        protocol_type = MXProtocolType.Super.SM_REFRESH

        self.thing_name = thing_name

        topic = protocol_type.value % (self.thing_name)
        payload = EMPTY_JSON
        super().__init__(topic=topic, payload=payload, protocol_type=protocol_type)


class MXHierarchyServiceTableResultMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.Super.MS_RESULT_SERVICE_LIST
        super().__init__(msg=msg, protocol_type=protocol_type)
        self.super_thing_name: str = self.topic.split('/')[3]
        self.service_list: List[dict] = self.payload['services']


class MXSuperScheduleMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.Super.MS_SCHEDULE
        super().__init__(msg=msg, protocol_type=protocol_type)

        # topic
        self.super_service_name = self.topic.split('/')[2]
        self.super_thing_name = self.topic.split('/')[3]
        self.super_middleware_name = self.topic.split('/')[4]
        self.requester_middleware_name = self.topic.split('/')[5]

        # payload
        self.scenario = self.payload['scenario']
        self.period = self.payload['period']

        if not isinstance(self.scenario, str) or not isinstance(self.period, (int, float)):
            self.payload_error = True

        # Call requester
        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )


class MXSuperScheduleResultMessage(MXMQTTSendMessage):

    def __init__(
        self,
        super_service_name: str,
        super_thing_name: str,
        super_middleware_name: str,
        requester_middleware_name: str,
        scenario: str,
        error: MXErrorCode = MXErrorCode.UNDEFINED,
    ) -> None:
        self.protocol_type = MXProtocolType.Super.SM_RESULT_SCHEDULE

        self.super_service_name = super_service_name
        self.super_thing_name = super_thing_name
        self.super_middleware_name = super_middleware_name
        self.requester_middleware_name = requester_middleware_name
        self.scenario = scenario
        self.error = error

        self.topic = self.protocol_type.value % (
            self.super_service_name,
            self.super_thing_name,
            self.super_middleware_name,
            self.requester_middleware_name,
        )
        self.payload = dict(scenario=self.scenario, error=self.error.value)
        super().__init__(topic=self.topic, payload=self.payload, protocol_type=self.protocol_type)

        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )


class MXSubScheduleMessage(MXMQTTSendMessage):

    def __init__(
        self,
        subservice_name: str,
        target_middleware_name: str,
        requester_middleware_name: str,
        line_num: int,
        super_thing_name: str = None,
        super_service_name: str = None,
        scenario: str = None,
        period: float = None,
        tag_list: List[str] = list(),
        range_type: MXRangeType = None,
        status: MXSchedulePhase = MXSchedulePhase.CHECK,
    ) -> None:
        self.protocol_type = MXProtocolType.Super.SM_SCHEDULE

        # topic
        self.subservice_name = subservice_name
        self.target_middleware_name = target_middleware_name
        self.requester_middleware_name = requester_middleware_name
        self.line_num = line_num

        self.super_thing_name = super_thing_name
        self.super_service_name = super_service_name
        self.scenario = scenario
        self.period = period
        self.tag_list = tag_list
        self.range_type = range_type

        self._phase = status

        self.request_ID = make_request_ID(
            self.requester_middleware_name,
            self.super_thing_name,
            self.super_service_name,
            self.line_num,
        )

        self.topic = self.protocol_type.value % (self.subservice_name, self.target_middleware_name, self.request_ID)
        self.payload = dict(
            scenario=self.scenario,
            period=self.period,
            status=self._phase.value,
            tag_list=self.tag_list,
            range=self.range_type.value,
        )
        super().__init__(topic=self.topic, payload=self.payload, protocol_type=self.protocol_type)

        # Requester & Target
        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )
        self.schedule_target: MXScheduleTarget = MXScheduleTarget(
            subservice=self.subservice_name,
            middleware=self.target_middleware_name,
            tag_list=self.tag_list,
            range_type=self.range_type,
        )

    # Getters and Setters
    @property
    def phase(self) -> MXSchedulePhase:
        return self._phase

    @phase.setter
    def phase(self, phase: MXSchedulePhase):
        if not isinstance(phase, MXSchedulePhase):
            raise MXTypeError("status must be an MXSchedulePhase")
        self._phase = phase
        self.payload = dict(
            scenario=self.scenario,
            period=self.period,
            status=self._phase.value,
            tag_list=self.tag_list,
            range=self.range_type.value,
        )


class MXSubScheduleResultMessage(MXMQTTReceiveMessage):

    def __init__(self, msg: MQTTMessage) -> None:
        self.protocol_type = MXProtocolType.Super.MS_RESULT_SCHEDULE
        super().__init__(msg=msg, protocol_type=self.protocol_type)

        # topic
        self.subservice_name = self.topic.split('/')[3]
        self.target_middleware_name = self.topic.split('/')[5]
        self.request_ID = self.topic.split('/')[6]

        self.requester_middleware_name = self.request_ID.split('@')[0]
        self.super_thing_name = self.request_ID.split('@')[1]
        self.super_service_name = self.request_ID.split('@')[2]
        self.line_num = int(self.request_ID.split('@')[3])

        # payload
        self.scenario = self.payload['scenario']
        self.error = MXErrorCode.get(self.payload['error'])
        self.phase = MXSchedulePhase.get(self.payload.get('status', None))  # 'check' or 'confirm'

        # Call requester & target
        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )
        self.schedule_target: MXScheduleTarget = MXScheduleTarget(
            subservice=self.subservice_name,
            middleware=self.target_middleware_name,
        )


class MXSuperExecuteMessage(MXMQTTReceiveMessage):

    def __init__(self, msg: MQTTMessage) -> None:
        self.protocol_type = MXProtocolType.Super.MS_EXECUTE
        super().__init__(msg=msg, protocol_type=self.protocol_type)

        # topic
        self.super_service_name = self.topic.split('/')[2]
        self.super_thing_name = self.topic.split('/')[3]
        self.super_middleware_name = self.topic.split('/')[4]
        self.requester_middleware_name = self.topic.split('/')[5]

        # payload
        self.scenario: str = self.payload.get('scenario', None)
        self.arguments: List[dict] = self.payload.get('arguments', None)

        if not self.scenario or self.arguments == None:
            self.payload_error = True
        elif not all([isinstance(arg.get('order', None), int) for arg in self.arguments]) or not all(
            [isinstance(arg.get('value', None), MXDataType) for arg in self.arguments]
        ):
            self.payload_error = True

        # Call requester
        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )

    def tuple_arguments(self) -> tuple:
        sorted_arguments = sorted(self.arguments, key=lambda x: int(x['order']))
        real_arguments = tuple([argument['value'] for argument in sorted_arguments])
        return real_arguments

    def dict_arguments(self) -> List[dict]:
        self.arguments = sorted(self.arguments, key=lambda x: int(x['order']))
        json_arguments = [dict(order=arg['order'], value=arg['value']) for arg in self.arguments]
        return json_arguments


class MXSuperExecuteResultMessage(MXMQTTSendMessage):

    def __init__(
        self,
        super_service_name: str,
        super_thing_name: str,
        super_middleware_name: str,
        requester_middleware_name: str,
        scenario: str,
        return_type: MXType,
        return_value: Union[int, float, bool, str] = None,
        error: MXErrorCode = MXErrorCode.UNDEFINED,
    ) -> None:
        self.protocol_type = MXProtocolType.Super.SM_RESULT_EXECUTE

        # payload
        self.super_service_name = super_service_name
        self.super_thing_name = super_thing_name
        self.super_middleware_name = super_middleware_name
        self.requester_middleware_name = requester_middleware_name
        self.scenario = scenario
        self.return_type = return_type
        self.return_value = return_value
        self._error = error
        self.action_type = MXActionType.SUPER_EXECUTE

        self.topic = self.protocol_type.value % (
            self.super_service_name,
            self.super_thing_name,
            self.super_middleware_name,
            self.requester_middleware_name,
        )
        self.payload = dict(scenario=self.scenario, return_type=self.return_type.value, return_value=self.return_value, error=self._error.value)
        super().__init__(topic=self.topic, payload=self.payload, protocol_type=self.protocol_type)

        # Call requester
        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )

    @property
    def error(self) -> dict:
        return self._error

    @error.setter
    def error(self, error: MXErrorCode):
        if not isinstance(error, MXErrorCode):
            raise MXTypeError("error must be an MXErrorType")
        self._error = error
        self.payload = dict(
            error=self._error.value,
            scenario=self.scenario,
            return_type=self.return_type.value,
            return_value=self.return_value,
        )


class MXSubExecuteMessage(MXMQTTSendMessage):

    def __init__(
        self,
        subservice_name: str,
        target_thing_name: str,
        target_middleware_name: str,
        line_num: int,
        execute_order: int,
        requester_middleware_name: str = None,
        super_thing_name: str = None,
        super_service_name: str = None,
        scenario: str = None,
        arguments: List[dict] = None,
    ) -> None:
        self.protocol_type = MXProtocolType.Super.SM_EXECUTE

        # topic
        self.subservice_name = subservice_name
        self.target_thing_name = target_thing_name
        self.target_middleware_name = target_middleware_name
        self.line_num = line_num
        self.execute_order = execute_order

        self.requester_middleware_name = requester_middleware_name
        self.super_thing_name = super_thing_name
        self.super_service_name = super_service_name

        self.scenario = scenario
        self._arguments = arguments

        self.request_ID = make_request_ID(
            self.requester_middleware_name,
            self.super_thing_name,
            self.super_service_name,
            self.line_num,
            self.execute_order,
        )

        self.topic = self.protocol_type.value % (self.subservice_name, self.target_middleware_name, self.request_ID)
        self.payload = dict(scenario=self.scenario, arguments=self._arguments)
        super().__init__(topic=self.topic, payload=self.payload, protocol_type=self.protocol_type)

        # Call requester & target
        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )
        self.execute_target: MXExecuteTarget = MXExecuteTarget(
            subservice=self.subservice_name,
            middleware=self.target_middleware_name,
            thing=self.target_thing_name,
        )

    # Getters and Setters
    @property
    def arguments(self) -> dict:
        return self._arguments

    @arguments.setter
    def arguments(self, arguments: tuple):
        if not isinstance(arguments, tuple):
            raise MXTypeError("arguments must be an tuple")
        self._arguments = arguments
        dict_arguments = [dict(order=i, value=arg) for i, arg in enumerate(self._arguments)]
        self.payload = dict(scenario=self.scenario, arguments=dict_arguments)

    # def json_arguments(self) -> List[dict]:
    #     self._arguments = sorted(self._arguments, key=lambda x: int(x['order']))
    #     json_arguments = [dict(order=arg['order'], value=arg['value']) for arg in self._arguments]
    #     return json_arguments


class MXSubExecuteResultMessage(MXMQTTReceiveMessage):

    def __init__(self, msg: MQTTMessage) -> None:
        self.protocol_type = MXProtocolType.Super.MS_RESULT_EXECUTE
        super().__init__(msg=msg, protocol_type=self.protocol_type)

        # topic
        self.subservice_name = self.topic.split('/')[3]
        self.target_thing_name = self.topic.split('/')[4]
        self.target_middleware_name = self.topic.split('/')[5]

        self.request_ID = self.topic.split('/')[6]
        self.requester_middleware_name = self.request_ID.split('@')[0]
        self.super_thing_name = self.request_ID.split('@')[1]
        self.super_service_name = self.request_ID.split('@')[2]
        self.line_num = int(self.request_ID.split('@')[3].split('-')[0])
        self.execute_order = int(self.request_ID.split('@')[3].split('-')[1])

        # payload
        self.scenario: str = self.payload['scenario']
        self.return_type = MXType.get(self.payload['return_type'])
        self.return_value: MXDataType = self.payload['return_value']  # TODO: 추후에 return_value -> return_values로 변경
        self._error = MXErrorCode.get(self.payload['error'])
        self.action_type = MXActionType.SUB_EXECUTE

        # Call requester & target
        self.call_requester: MXCallRequester = MXCallRequester(
            middleware=self.requester_middleware_name,
            scenario=self.scenario,
        )
        self.execute_target: MXExecuteTarget = MXExecuteTarget(
            subservice=self.subservice_name,
            middleware=self.target_middleware_name,
            thing=self.target_thing_name,
        )

    @property
    def error(self) -> dict:
        return self._error

    @error.setter
    def error(self, error: MXErrorCode):
        if not isinstance(error, MXErrorCode):
            raise MXTypeError("error must be an MXErrorType")
        self._error = error
        self.payload = dict(
            error=self._error.value,
            scenario=self.scenario,
            return_type=self.return_type.value,
            return_value=self.return_value,
        )
