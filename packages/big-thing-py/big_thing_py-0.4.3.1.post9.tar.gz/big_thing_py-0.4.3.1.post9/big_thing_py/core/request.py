from big_thing_py.common.mxtype import *
from big_thing_py.core.mqtt_message import *


class MXRequest(metaclass=ABCMeta):
    def __init__(self, trigger_msg: MXMQTTMessage = None, result_msg: MXMQTTMessage = None) -> None:
        self.action_type: MXActionType = None
        self.trigger_msg = trigger_msg
        self.result_msg = result_msg

        self._duration: float = 0

    def timer_start(self) -> None:
        self.trigger_msg.set_timestamp()

    def timer_end(self) -> None:
        self.result_msg.set_timestamp()
        self._duration = self.result_msg.timestamp - self.trigger_msg.timestamp

    @property
    def duration(self) -> float:
        if self.trigger_msg.timestamp == None:
            return 0
        elif self.result_msg.timestamp == None:
            return get_current_datetime(TimeFormat.UNIXTIME) - self.trigger_msg.timestamp
        else:
            return self.result_msg.timestamp - self.trigger_msg.timestamp


class MXRegisterRequest(MXRequest):

    def __init__(self, trigger_msg: MXRegisterMessage = None, result_msg: MXRegisterResultMessage = None) -> None:
        super().__init__(trigger_msg=trigger_msg, result_msg=result_msg)
        self.action_type = MXActionType.REGISTER

        self.trigger_msg: MXRegisterMessage
        self.result_msg: MXRegisterResultMessage


class MXExecuteRequest(MXRequest):
    def __init__(self, trigger_msg: MXExecuteMessage = None, result_msg: MXExecuteResultMessage = None) -> None:
        super().__init__(trigger_msg=trigger_msg, result_msg=result_msg)
        self.action_type = MXActionType.EXECUTE

        self.trigger_msg: MXExecuteMessage
        self.result_msg: MXExecuteResultMessage


class MXInnerExecuteRequest(MXRequest):
    def __init__(self, trigger_msg: MXExecuteMessage = None, result_msg: MXExecuteResultMessage = None) -> None:
        super().__init__(trigger_msg=trigger_msg, result_msg=result_msg)
        self.action_type = MXActionType.INNER_EXECUTE

        self.trigger_msg: MXExecuteMessage
        self.result_msg: MXExecuteResultMessage
