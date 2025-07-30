from big_thing_py.super.super_request import *
from big_thing_py.super.super_mqtt_message import *

import threading
import random
from typing import Awaitable, Optional, Callable, Any, Protocol, TypedDict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..super.helper.util import *


# The list order is the same as call_line_info_list order
MappingTableType: TypeAlias = Dict[MXCallRequester, Dict[int, List[MXExecuteTarget]]]
FutureScheduleTableType: TypeAlias = Dict[MXCallRequester, Dict[int, asyncio.Future]]
FutureExecuteTableType: TypeAlias = Dict[MXCallRequester, Dict[int, Dict[int, asyncio.Future]]]


class CreateCallLineScheduleTask(Protocol):

    def __call__(
        self,
        target_super_function: 'MXSuperFunction',
        call_line_info: MXCallLineInfo,
        super_schedule_request: MXSuperScheduleRequest,
        hierarchical_service_table: Dict[str, List[MXService]],
    ) -> asyncio.Task[List[MXScheduleTarget]]: ...


class CreateCallLineExecuteTask(Protocol):

    def __call__(
        self,
        target_super_function: 'MXSuperFunction',
        call_line_info: MXCallLineInfo,
        super_execute_request: MXSuperExecuteRequest,
    ) -> asyncio.Task[List[MXDataType]]: ...


class CreateSubScheduleTask(Protocol):

    def __call__(
        self,
        target_super_function: 'MXSuperFunction',
        subschedule_request: MXSubScheduleRequest,
    ) -> asyncio.Task[MXScheduleTarget]: ...


class CreateSubExecuteTask(Protocol):

    def __call__(
        self,
        target_super_function: 'MXSuperFunction',
        subexecute_request: MXSubExecuteRequest,
    ) -> asyncio.Task[MXExecuteTarget]: ...


class Publish(Protocol):
    def __call__(
        self,
        topic: str,
        payload: dict,
    ) -> MQTTMessage: ...


class MXSuperFunction(MXFunction):
    '''
    [Whole super service structure]
    super_thing ─┬─ super_service1 ─┬─ subservice1 ─┬─ target_thing1(@Middleware1)
                 │                  │               │
                 │                  ├─ subservice2  ├─ target_thing2(@Middleware1)
                 │                  │               │
                 │                  ├─ ...          ├─ target_thing3(@Middleware2)
                 │                                  │
                 │                                  ├─ ...
                 │
                 └─ super_service2 ─── subservice3 ─┬─ target_thing1(@Middleware2)
                                                    │
                                                    ├─ ...
    '''

    def __init__(
        self,
        func: Callable,
        return_type: MXType,
        name: str = '',
        tag_list: List[MXTag] = list(),
        energy: float = 0,
        desc: str = '',
        thing_name: str = '',
        middleware_name: str = '',
        arg_list: List[MXArgument] = list(),
        exec_time: float = 0,
        timeout: float = 0,
        range_type: MXRangeType = MXRangeType.SINGLE,
    ) -> None:
        super().__init__(
            func=func,
            return_type=return_type,
            name=name,
            tag_list=tag_list,
            energy=energy,
            desc=desc,
            thing_name=thing_name,
            middleware_name=middleware_name,
            arg_list=arg_list,
            exec_time=exec_time,
            timeout=timeout,
            range_type=range_type,
        )

        self._schedule_running: bool = False
        self._call_line_info_list: List[MXCallLineInfo] = getattr(self._func, CALL_LINE_INFO_LIST_ATTRIBUTE, None)

        # MXReqType에 대한 scheduling 결과를 저장하기 위한 테이블.
        # _temp_mapping_table에는 check 단계에서 확정되기전의 매핑 정보가 저장된다.
        # _mapping_table에는 confirm을 통해 확정된 매핑 정보가 저장된다.
        #
        #   MXCallRequester: 어떤 미들웨어의 시나리오가 호출하는지
        #   MXExecuteTarget: 어떤 미들웨어의 thing에 대한 요청인지
        #
        # [Structure]
        # {
        #     MXCallRequester: {
        #         "subservice": [
        #             MXExecuteTarget,
        #             ...
        #         ],
        #         ...
        #     },
        #     ...
        # }
        self._mapping_table: MappingTableType = {}

        # create task function
        self._create_call_line_schedule_task: CreateCallLineScheduleTask = None
        self._create_subschedule_task: CreateSubScheduleTask = None
        self._create_call_line_execute_task: CreateCallLineExecuteTask = None
        self._create_subexecute_task: CreateSubExecuteTask = None
        self._publish: Publish = None

        # MS_RESULT_* 에 대한 결과를 받기 위한 future list
        #
        # [Structure]
        # {
        #     MXCallRequester: {
        #         MXExecuteTarget | MXScheduleTarget: asyncio.Future(),
        #         ...
        #     },
        #     ...
        # }
        self.super_schedule_future_table: FutureScheduleTableType = {}
        self.super_execute_future_table: FutureExecuteTableType = {}

    def __eq__(self, o: 'MXFunction') -> bool:
        instance_check = isinstance(o, MXFunction)

        return super().__eq__(o) and instance_check

    def __getstate__(self):
        state = super().__getstate__()

        state['_mapping_table'] = self._mapping_table

        del state['_schedule_running']

        return state

    def __setstate__(self, state):
        super().__setstate__(state)

        self._mapping_table = state['_mapping_table']

        self._schedule_running = False

    async def super_schedule(
        self,
        super_schedule_request: MXSuperScheduleRequest,
        hierarchical_service_table: Dict[str, List[MXService]],
    ) -> List[List[MXSubScheduleRequest]]:
        '''
        super service의 하위 함수에 대한 정보를 추출한다.
        service_list 구조는

        ============================================
        super_service -> sub_function_type_list
                      -> sub_function_list
        ============================================

        로 이루어져있다.
        sub_function_type_list과 sub_function_list는 독립적인 공간을 가진다.
        super_service 내부에 req함수 가 존재하여 사용자가 요청하고 싶은 subservice이 명세되어있는데 여기서 명세되어지는
        subservice은 실제 타겟 subservice이 아닌 subservice_type이다. 실제 subservice 정보는 middleware로 부터 받은
        service_list를 통해 추출한다. 그리고 해당 정보는 super_service의 subservice_list에 저장된다.
        '''
        if not isinstance(super_schedule_request, MXSuperScheduleRequest):
            raise MXTypeError(f'[{get_current_function_name()}] Wrong Request type: {type(super_schedule_request)}')

        super_schedule_request.timer_start()

        self._schedule_running = True

        MXLOG_INFO(
            f'[{super_schedule_request.action_type.name} START] {self._name} by scenario {super_schedule_request.trigger_msg.scenario}.', success=True
        )

        call_requester = super_schedule_request.trigger_msg.call_requester
        if call_requester not in self.super_schedule_future_table:
            self.super_schedule_future_table[call_requester] = {}

        requester_schedule_result: Dict[int, List[MXScheduleTarget]] = {}
        for i, call_line_info in enumerate(self._call_line_info_list):
            call_line_schedule_result = await self._create_call_line_schedule_task(
                target_super_function=self,
                call_line_info=call_line_info,
                super_schedule_request=super_schedule_request,
                hierarchical_service_table=hierarchical_service_table,
            )
            requester_schedule_result[i] = call_line_schedule_result

        return requester_schedule_result

    async def call_line_schedule(
        self,
        call_line_info: MXCallLineInfo,
        super_schedule_request: MXSuperScheduleRequest,
        hierarchical_service_table: Dict[str, List[MXService]],
    ) -> List[MXScheduleTarget]:
        super_schedule_msg = super_schedule_request.trigger_msg
        call_requester = super_schedule_msg.call_requester

        candidate_schedule_target_list = get_candidate_list(
            call_line_info=call_line_info,
            hierarchical_service_table=hierarchical_service_table,
            action_type=MXActionType.SUB_SCHEDULE,
        )

        # Check phase
        task_list = []
        for candidate in candidate_schedule_target_list:
            subschedule_request = MXSubScheduleRequest(
                trigger_msg=MXSubScheduleMessage(
                    subservice_name=candidate.subservice,
                    target_middleware_name=candidate.middleware,
                    requester_middleware_name=super_schedule_msg.requester_middleware_name,
                    line_num=call_line_info.line_num,
                    super_thing_name=super_schedule_msg.super_thing_name,
                    super_service_name=super_schedule_msg.super_service_name,
                    scenario=super_schedule_msg.scenario,
                    period=super_schedule_msg.period,
                    tag_list=call_line_info.tag_list,
                    range_type=call_line_info.range_type,
                    status=MXSchedulePhase.CHECK,
                ),
                result_msg=None,
            )
            task = self._create_subschedule_task(
                target_super_function=self,
                subschedule_request=subschedule_request,
            )
            task_list.append(task)
        call_line_schedule_result_list: List[MXSubScheduleResultMessage] = await asyncio.gather(*task_list)
        checked_target_list = [result.schedule_target for result in call_line_schedule_result_list]

        # Select phase
        selected_target_list = self.select_target(checked_target_list, range_type=call_line_info.range_type)

        # Confirm phase
        task_list = []
        for selected_target in selected_target_list:
            if call_requester not in self.super_schedule_future_table:
                self.super_schedule_future_table[call_requester] = {}

            subschedule_request = MXSubScheduleRequest(
                trigger_msg=MXSubScheduleMessage(
                    subservice_name=selected_target.subservice,
                    target_middleware_name=selected_target.middleware,
                    requester_middleware_name=super_schedule_msg.requester_middleware_name,
                    line_num=call_line_info.line_num,
                    super_thing_name=super_schedule_msg.super_thing_name,
                    super_service_name=super_schedule_msg.super_service_name,
                    scenario=super_schedule_msg.scenario,
                    period=super_schedule_msg.period,
                    tag_list=call_line_info.tag_list,
                    range_type=call_line_info.range_type,
                    status=MXSchedulePhase.CONFIRM,
                ),
                result_msg=None,
            )

            task = self._create_subschedule_task(
                target_super_function=self,
                subschedule_request=subschedule_request,
            )
            task_list.append(task)
        call_line_schedule_result_list: List[MXSubScheduleResultMessage] = await asyncio.gather(*task_list)
        confirmed_target_list = [result.schedule_target for result in call_line_schedule_result_list]

        return confirmed_target_list

    async def subservice_schedule(
        self,
        subschedule_request: MXSubScheduleRequest,
    ) -> MXSubScheduleRequest:
        subschedule_request.timer_start()

        subschedule_msg = subschedule_request.trigger_msg
        call_requester = subschedule_msg.call_requester
        MXLOG_DEBUG(
            f'[SUB_SCHEDULE {subschedule_msg.phase.name} START] '
            f'{subschedule_msg.subservice_name}|{subschedule_msg.target_middleware_name}|'
            'cyan',
        )

        self._publish(
            topic=subschedule_request.trigger_msg.topic,
            payload=subschedule_request.trigger_msg.payload,
        )

        # Wait for receive MS_RESULT_SCHEDULE packet
        future = asyncio.Future()
        line_num = subschedule_request.trigger_msg.line_num
        self.super_schedule_future_table[call_requester][line_num] = future
        result_msg = await future
        subschedule_request.result_msg = result_msg

        subschedule_request.timer_end()

        return subschedule_request.result_msg

    async def super_execute(
        self,
        super_execute_request: MXSuperExecuteRequest,
    ) -> MXDataType:
        if not isinstance(super_execute_request, MXSuperExecuteRequest):
            raise MXTypeError(f'[{get_current_function_name()}] Wrong Request type: {type(super_execute_request)}')

        super_execute_request.timer_start()

        self._running = True

        # call()이 현재 몇번째 call()인지 인식할 수 있게 하기 위해 설정
        call_requester = super_execute_request.trigger_msg.call_requester
        setattr(self._func, LINE_NUM_ATTRIBUTE, 0)
        setattr(self._func, SUPER_EXECUTE_REQUEST_ATTRIBUTE, super_execute_request)
        setattr(self._func, SELF_ATTRIBUTE, self)

        execute_msg = super_execute_request.trigger_msg
        self._running_scenario_list.append(execute_msg.scenario)
        MXLOG_DEBUG(f'[{super_execute_request.action_type.name} START] {self._name} by requester {call_requester}.', 'green')

        async def async_wrapper(func: Callable, *args: List[MXDataType]) -> MXDataType:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: func(*args))

        if not call_requester in self.super_execute_future_table:
            self.super_execute_future_table[call_requester] = {}

        if asyncio.iscoroutinefunction(self._func):
            result = await self._func(*execute_msg.tuple_arguments())
        else:
            result = await async_wrapper(self._func, *execute_msg.tuple_arguments())

        return result

    async def call_line_execute(
        self,
        call_line_info: MXCallLineInfo,
        super_execute_request: MXSuperExecuteRequest,
    ) -> List[List[MXDataType]]:
        super_execute_msg = super_execute_request.trigger_msg
        call_requester = super_execute_msg.call_requester

        task_list = []
        for i, target in enumerate(self._mapping_table[call_requester][call_line_info.line_num]):
            if call_line_info.line_num not in self.super_execute_future_table[call_requester]:
                self.super_execute_future_table[call_requester][call_line_info.line_num] = {}

            task = self._create_subexecute_task(
                target_super_function=self,
                subexecute_request=MXSubExecuteRequest(
                    trigger_msg=MXSubExecuteMessage(
                        subservice_name=call_line_info.subservice,
                        target_thing_name=target.thing,
                        target_middleware_name=target.middleware,
                        line_num=call_line_info.line_num,
                        execute_order=i,
                        requester_middleware_name=super_execute_msg.requester_middleware_name,
                        super_thing_name=super_execute_msg.super_thing_name,
                        super_service_name=super_execute_msg.super_service_name,
                        scenario=super_execute_msg.scenario,
                        arguments=super_execute_msg.arguments,
                    ),
                    result_msg=None,
                ),
            )
            task_list.append(task)
        call_line_execute_result_list: List[MXSubExecuteResultMessage] = await asyncio.gather(*task_list)
        return_value_list = [result.return_value for result in call_line_execute_result_list]

        return return_value_list

    async def subservice_execute(
        self,
        subexecute_request: MXSubExecuteRequest,
    ):
        subexecute_msg = subexecute_request.trigger_msg
        call_requester = subexecute_msg.call_requester
        MXLOG_DEBUG(
            f'[SUB_EXECUTE {subexecute_msg.subservice_name}|{subexecute_msg.line_num}-{subexecute_msg.execute_order} START] '
            f'{subexecute_msg.subservice_name}|{subexecute_msg.target_thing_name}|'
            f'{subexecute_msg.target_middleware_name}',
            'cyan',
        )

        self._publish(
            topic=subexecute_request.trigger_msg.topic,
            payload=subexecute_request.trigger_msg.payload,
        )

        # Wait for receive MS_RESULT_EXECUTE packet
        future = asyncio.Future()
        line_num = subexecute_request.trigger_msg.line_num
        execute_order = subexecute_request.trigger_msg.execute_order
        self.super_execute_future_table[call_requester][line_num][execute_order] = future
        result = await future
        return result

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    def super_schedule_result_message(self):
        schedule_result_string = '\n[SUPER_SCHEDULE RESULT] ============================================\n'

        # self._mapping_table: Dict[MXCallRequester, Dict[str, List[MXScheduleTarget | MXExecuteTarget]]]
        for call_requester, target_table in self._mapping_table.items():
            schedule_result_string += f'Scheduling by requester: {call_requester}\n'
            schedule_result_string += f'super_service: {self._name}\n'
            for subservice, target_list in target_table.items():
                schedule_result_string += TAB + f'subservice: {subservice}\n'
                for target in target_list:
                    schedule_result_string += TAB * 2 + f'target: {target}\n'
        schedule_result_string += '==============================================================\n'

    def super_execute_result_message(self):
        execute_result_string = '\n[SUPER_EXECUTE RESULT] ============================================\n'

        # self._mapping_table: Dict[MXCallRequester, Dict[str, List[MXScheduleTarget | MXExecuteTarget]]]
        for call_requester, target_table in self._mapping_table.items():
            execute_result_string += f'Execution by requester: {call_requester}\n'
            execute_result_string += f'super_service: {self._name}\n'
            for subservice, target_list in target_table.items():
                execute_result_string += TAB + f'subservice: {subservice}\n'
                for target in target_list:
                    execute_result_string += TAB * 2 + f'target: {target}\n'
        execute_result_string += '==============================================================\n'

    def select_target(
        self, target_list: List[MXScheduleTarget | MXExecuteTarget], range_type: MXRangeType
    ) -> List[MXScheduleTarget | MXExecuteTarget]:
        policy = lambda x: [x[0]]
        # policy = lambda x: [random.choice(x)]

        if range_type == MXRangeType.SINGLE:
            return policy(target_list)
        elif range_type == MXRangeType.ALL:
            return target_list
        else:
            raise MXTypeError(f'[{get_current_function_name()}] Wrong Range Type: {range_type}')

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
    def schedule_running(self) -> bool:
        return self._schedule_running

    @property
    def call_line_info_list(self) -> List[MXCallLineInfo]:
        return self._call_line_info_list

    @property
    def mapping_table(self) -> MappingTableType:
        return self._mapping_table

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @schedule_running.setter
    def schedule_running(self, schedule_running: bool):
        self._schedule_running = schedule_running

    @call_line_info_list.setter
    def call_line_info_list(self, call_line_info_list: List[MXCallLineInfo]):
        self._call_line_info_list = call_line_info_list
