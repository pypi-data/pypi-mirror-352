from big_thing_py.core.request import *
from big_thing_py.super.super_mqtt_message import *
from big_thing_py.core.function import *


class MXSuperScheduleRequest(MXRequest):

    def __init__(self, trigger_msg: MXSuperScheduleMessage = None, result_msg: MXSuperScheduleResultMessage = None) -> None:
        super().__init__(trigger_msg=trigger_msg, result_msg=result_msg)
        self.action_type = MXActionType.SUPER_SCHEDULE

        self.trigger_msg: MXSuperScheduleMessage
        self.result_msg: MXSuperScheduleResultMessage
        self.check_duration: float = 0.0
        self.confirm_duration: float = 0.0


class MXSubScheduleRequest(MXRequest):

    def __init__(self, trigger_msg: MXSubScheduleMessage = None, result_msg: MXSubScheduleResultMessage = None) -> None:
        super().__init__(trigger_msg=trigger_msg, result_msg=result_msg)
        self.action_type = MXActionType.SUB_SCHEDULE

        self.trigger_msg: MXSubScheduleMessage
        self.result_msg: MXSubScheduleResultMessage
        self._status: MXScheduleStatus = None

    @property
    def status(self) -> MXScheduleStatus:
        if self.trigger_msg == None and self.result_msg == None:
            status = MXScheduleStatus.INIT
        elif self.trigger_msg and self.result_msg == None:
            status = MXScheduleStatus.CHECK_PENDING
        elif self.trigger_msg.phase == MXSchedulePhase.CHECK and self.result_msg.phase == MXSchedulePhase.CHECK:
            status = MXScheduleStatus.CHECKED
        elif self.trigger_msg.phase == MXSchedulePhase.CONFIRM and self.result_msg.phase == MXSchedulePhase.CHECK:
            status = MXScheduleStatus.CONFIRM_PENDING
        elif self.trigger_msg.phase == MXSchedulePhase.CONFIRM and self.result_msg.phase == MXSchedulePhase.CONFIRM:
            status = MXScheduleStatus.CONFIRMED
        else:
            status = MXScheduleStatus.UNDEFINED

        return status


class MXSuperExecuteRequest(MXRequest):
    def __init__(self, trigger_msg: MXSuperExecuteMessage = None, result_msg: MXSuperExecuteResultMessage = None) -> None:
        super().__init__(trigger_msg=trigger_msg, result_msg=result_msg)
        self.action_type = MXActionType.SUPER_EXECUTE

        self.trigger_msg: MXSuperExecuteMessage
        self.result_msg: MXSuperExecuteResultMessage


class MXSubExecuteRequest(MXRequest):

    def __init__(self, trigger_msg: MXSubExecuteMessage = None, result_msg: MXSubExecuteResultMessage = None) -> None:
        super().__init__(trigger_msg=trigger_msg, result_msg=result_msg)
        self.action_type = MXActionType.SUB_EXECUTE

        self.trigger_msg: MXSubExecuteMessage
        self.result_msg: MXSubExecuteResultMessage

    ################################################################


# ========================
#         _    _  _
#        | |  (_)| |
#  _   _ | |_  _ | | ___
# | | | || __|| || |/ __|
# | |_| || |_ | || |\__ \
#  \__,_| \__||_||_||___/
# ========================
