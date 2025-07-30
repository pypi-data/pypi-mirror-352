from big_thing_py.utils import *
from big_thing_py.core.argument import MXArgumentData


class MXMQTTMessage:
    def __init__(self, protocol_type: Union[MXProtocolType.Base, MXProtocolType.Super, MXProtocolType.WebClient]) -> None:
        self.protocol_type = protocol_type
        self.topic: str = None
        self.timestamp: float = None

        self.topic_error: bool = False
        self.payload_error: bool = False

    def set_timestamp(self, timestamp: float = None) -> None:
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = get_current_datetime(TimeFormat.UNIXTIME)


class MXMQTTSendMessage(MXMQTTMessage):
    def __init__(self, topic: str, payload: dict, protocol_type: Union[MXProtocolType.Base, MXProtocolType.Super, MXProtocolType.WebClient]) -> None:
        super().__init__(protocol_type)
        self.topic = topic
        self.payload = payload

        if MXProtocolType.get(self.topic) != self.protocol_type:
            self.topic_error = True
        else:
            self.topic_error = False

    def mqtt_message(self) -> MQTTMessage:
        msg = encode_MQTT_message(self.topic, self.payload)
        return msg


class MXMQTTReceiveMessage(MXMQTTMessage):
    def __init__(self, msg: MQTTMessage, protocol_type: Union[MXProtocolType.Base, MXProtocolType.Super, MXProtocolType.WebClient]) -> None:
        super().__init__(protocol_type)
        self.topic, self.payload = decode_MQTT_message(msg)

        if MXProtocolType.get(self.topic) != self.protocol_type:
            self.topic_error = True
        else:
            self.topic_error = False


##############################################################################################################################


class MXRegisterMessage(MXMQTTSendMessage):
    def __init__(self, thing_name: str, payload: dict) -> None:
        protocol_type = MXProtocolType.Base.TM_REGISTER

        self.thing_name = thing_name

        topic = protocol_type.value % (self.thing_name)
        super().__init__(topic=topic, payload=payload, protocol_type=protocol_type)


class MXRequestRegisterInfoMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.Base.MT_REQUEST_REGISTER_INFO
        super().__init__(msg=msg, protocol_type=protocol_type)

        self.middleware_name = self.topic.split('/')[2]
        self.error: MXErrorCode = None

        self.client_id: str = self.payload.get('client_id', None)
        if self.client_id is None:
            self.payload_error = True


class MXRequestUnregisterMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.Base.MT_REQUEST_UNREGISTER
        super().__init__(msg=msg, protocol_type=protocol_type)

        self.middleware_name = self.topic.split('/')[2]
        self.error: MXErrorCode = None

        self.client_id: str = self.payload.get('client_id', None)
        if self.client_id is None:
            self.payload_error = True


class MXRegisterResultMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.Base.MT_RESULT_REGISTER
        super().__init__(msg=msg, protocol_type=protocol_type)

        self.thing_name = self.topic.split('/')[3]
        self.middleware_name: str = self.payload['middleware_name']
        self.error: MXErrorCode = MXErrorCode.get(self.payload['error'])


class MXUnregisterMessage(MXMQTTSendMessage):
    def __init__(self, thing_name: str, client_id: str = '') -> None:
        protocol_type = MXProtocolType.Base.TM_UNREGISTER

        self.thing_name = thing_name
        self.client_id = client_id

        topic = protocol_type.value % (self.thing_name)
        payload = dict(client_id=self.client_id)
        super().__init__(topic=topic, payload=payload, protocol_type=protocol_type)


class MXUnregisterResultMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.Base.MT_RESULT_UNREGISTER
        super().__init__(msg=msg, protocol_type=protocol_type)
        self.thing_name: str = self.topic.split('/')[3]
        self.error: MXErrorCode = MXErrorCode.get(self.payload['error'])


class MXExecuteMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.get(msg.topic.decode())
        super().__init__(msg=msg, protocol_type=protocol_type)

        if self.protocol_type in [MXProtocolType.Base.MT_EXECUTE, MXProtocolType.Base.MT_IN_EXECUTE]:
            self.topic_error = False
        else:
            self.topic_error = True
            return

        self.middleware_name: str = ''
        self.request_ID: str = ''
        self.client_id: str = ''

        if self.protocol_type == MXProtocolType.Base.MT_EXECUTE:
            self.function_name: str = self.topic.split('/')[2]
            self.thing_name: str = self.topic.split('/')[3]

            if len(self.topic.split('/')) == 6:
                # MT/EXECUTE/[FunctionName]/[ThingName]/[TargetMiddlewareName]/[Request_ID] topic
                self.middleware_name: str = self.topic.split('/')[4]
                self.request_ID: str = self.topic.split('/')[5]
                if not self.middleware_name or not self.request_ID:
                    self.topic_error = True
            elif len(self.topic.split('/')) == 4:
                # MT/EXECUTE/[FunctionName]/[ThingName] topic
                self.middleware_name: str = ''
                self.request_ID: str = ''
            else:
                self.topic_error = True
        elif self.protocol_type == MXProtocolType.Base.MT_IN_EXECUTE:
            self.function_name: str = self.topic.split('/')[3]
            self.thing_name: str = self.topic.split('/')[4]
            self.middleware_name: str = ''
            self.request_ID: str = ''

        self.scenario: str = self.payload.get('scenario', '')
        self.arguments: List[MXArgumentData] = [MXArgumentData(arg['order'], arg['value']) for arg in self.payload.get('arguments', [])]
        self.client_id: str = self.payload.get('client_id', '')

        if not self.scenario or self.arguments == None:
            self.payload_error = True

    def tuple_arguments(self) -> tuple:
        self.arguments = sorted(self.arguments, key=lambda x: int(x.order))
        real_arguments = tuple([argument.data for argument in self.arguments])
        return real_arguments

    def dict_arguments(self) -> List[dict]:
        self.arguments = sorted(self.arguments, key=lambda x: int(x.order))
        json_arguments = [dict(order=arg.order, value=arg.data) for arg in self.arguments]
        return json_arguments


class MXExecuteResultMessage(MXMQTTSendMessage):

    def __init__(
        self,
        function_name: str = '',
        thing_name: str = '',
        middleware_name: str = '',
        scenario: str = '',
        client_id: str = '',
        request_ID: str = '',
        return_type: MXType = MXType.UNDEFINED,
        return_value: MXDataType = None,
        updated_value: str = '',
        value_update_to: MXDataType = None,
        error: MXErrorCode = MXErrorCode.UNDEFINED,
        action_type: MXActionType = MXActionType.EXECUTE,
    ) -> None:
        if action_type == MXActionType.EXECUTE:
            protocol_type = MXProtocolType.Base.TM_RESULT_EXECUTE
        elif action_type == MXActionType.INNER_EXECUTE:
            protocol_type = MXProtocolType.Base.TM_IN_RESULT_EXECUTE
        else:
            self.topic_error = True
            return

        self.function_name = function_name
        self.thing_name = thing_name
        self.middleware_name = middleware_name
        self.scenario = scenario
        self.client_id = client_id
        self.request_ID = request_ID
        self.return_type = return_type
        self.return_value = return_value
        self.updated_value = updated_value
        self.value_update_to = value_update_to

        self._error = error
        self.action_type = action_type

        if self.request_ID:
            topic = protocol_type.value % (
                self.function_name,
                self.thing_name,
                self.middleware_name,
                self.request_ID,
            )
        else:
            if self.action_type == MXActionType.EXECUTE:
                topic = (protocol_type.value % (self.function_name, self.thing_name, '', '')).rstrip('/')
            elif self.action_type == MXActionType.INNER_EXECUTE:
                topic = protocol_type.value % (self.function_name, self.thing_name)

        if self.action_type == MXActionType.EXECUTE:
            payload = dict(
                error=self._error.value,
                scenario=self.scenario,
                return_type=self.return_type.value,
                return_value=self.return_value,
            )
        elif self.action_type == MXActionType.INNER_EXECUTE:
            payload = dict(
                error=self._error.value,
                scenario=self.scenario,
                client_id=self.client_id,
                return_type=self.return_type.value,
                return_value=self.return_value,
            )

        super().__init__(topic=topic, payload=payload, protocol_type=protocol_type)

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


# TODO: binary 부분 구현 완료 후 작성하기
class MXBinaryValueResultMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.Base.MT_RESULT_BINARY_VALUE
        super().__init__(msg=msg, protocol_type=protocol_type)
        self.thing_name = self.topic.split('/')[3]
        self.value_name = self.payload['value']


class MXAliveMessage(MXMQTTSendMessage):
    def __init__(self, thing_name: str) -> None:
        protocol_type = MXProtocolType.Base.TM_ALIVE

        self.thing_name = thing_name

        topic = protocol_type.value % (self.thing_name)
        payload = EMPTY_JSON
        super().__init__(topic=topic, payload=payload, protocol_type=protocol_type)


class MXValuePublishMessage(MXMQTTSendMessage):
    def __init__(self, value_name: str, thing_name: str, payload: dict) -> None:
        protocol_type = MXProtocolType.Base.TM_VALUE_PUBLISH

        self.value_name = value_name
        self.thing_name = thing_name

        topic = protocol_type.value % (self.value_name, self.thing_name)
        super().__init__(topic=topic, payload=payload, protocol_type=protocol_type)


# for middleware detect
class MXHomeResultMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.WebClient.ME_RESULT_HOME
        super().__init__(msg=msg, protocol_type=protocol_type)
        self._client_id = self.topic.split('/')[3]


class MXGetHomeMessage(MXMQTTSendMessage):
    def __init__(self, thing_name: str) -> None:
        protocol_type = MXProtocolType.WebClient.EM_GET_HOME

        self.thing_name = thing_name

        topic = protocol_type.value % (self.thing_name)
        payload = EMPTY_JSON
        super().__init__(topic=topic, payload=payload, protocol_type=protocol_type)


class MXNotifyMessage(MXMQTTReceiveMessage):
    def __init__(self, msg: MQTTMessage) -> None:
        protocol_type = MXProtocolType.WebClient.ME_NOTIFY_CHANGE
        super().__init__(msg=msg, protocol_type=protocol_type)

        # topic
        self._client_id = self.topic.split('/')[2]

        # payload


if __name__ == '__main__':
    payload = {
        'scenario': 'test',
        'arguments': [
            {
                'order': 0,
                'value': 1,
            },
            {
                'order': 1,
                'value': 2,
            },
        ],
    }
    msg = encode_MQTT_message('MT/EXECUTE/test1/test2', payload)
    message = MXExecuteMessage(msg)
    print(message.tuple_arguments())
    print(message.dict_arguments(*(1, 2)))
