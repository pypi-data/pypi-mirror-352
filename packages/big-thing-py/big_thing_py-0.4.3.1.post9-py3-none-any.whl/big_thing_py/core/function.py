from big_thing_py.common import *
from big_thing_py.core.request import *
from big_thing_py.core.mqtt_message import *
from big_thing_py.core.argument import *
from big_thing_py.core.service import *
from big_thing_py.core.service_model import SkillFunction, SkillFunctionArgument
from big_thing_py.core.service_model import Objects as Skill
from big_thing_py.core.value import MXValue

import asyncio
from typing import TypedDict


class ValueUpdateMap(TypedDict):
    value: MXValue
    callback: Optional[Callable[..., MXDataType] | Callable[..., Coroutine[Any, Any, MXDataType]]]


class MXFunction(MXService):

    def __init__(
        self,
        func: Callable,
        tag_list: List[MXTag],
        return_type: MXType = None,
        category: Union[SkillValue, SkillFunction] = None,
        name: str = '',
        energy: float = 0,
        desc: str = '',
        thing_name: str = '',
        middleware_name: str = '',
        arg_list: List[MXArgument] = None,
        exec_time: float = 0,
        timeout: float = 0,
        range_type: MXRangeType = MXRangeType.SINGLE,
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

        # Check return type and Set argument list
        if self._category != None:
            # NOTE (thsvkd): generate getter MXFunction instance of target MXValue
            if issubclass(self._category, SkillValue):
                self._return_type = normalize_mx_type(self._category.value_type.type)
                self._arg_list = []
            elif issubclass(self._category, SkillFunction):
                if arg_list:
                    MXLOG_INFO('`arg_list` parameter will be ignored because category is given')

                self._return_type = normalize_mx_type(self._category.return_type)
                arguments: List[SkillFunctionArgument] = self._category.arguments
                self._arg_list = [
                    MXArgument(
                        name=arg.argument_id,
                        type=arg.argument_type.type,
                        bound=arg.argument_type.bound,
                    )
                    for arg in arguments
                ]
        else:
            if not return_type:
                func_info = get_function_info(self._func)
                return_type = MXType.get(func_info['return_type'])
                self._return_type = normalize_mx_type(return_type)
            else:
                self._return_type = normalize_mx_type(return_type)

            self._arg_list = arg_list

        if self._arg_list == None:
            self._arg_list = []

        # Set function name of arguments
        for arg in self._arg_list:
            arg.function_name = self._name

        self._exec_time = exec_time
        self._timeout = timeout
        # TODO: range_type will be removed from MXFunction
        self._range_type = range_type

        self._return_value = None
        self._running = False
        self._running_scenario_list: List[str] = []
        self._value_update_map: Dict[str, ValueUpdateMap] = {}

        # Check return type is valid
        if self._return_type in [MXType.UNDEFINED] or isinstance(self._return_type, str):
            raise MXValueError('return_type cannot be undefined or `str` type')

        # Check argument list is valid
        if (not len(self._arg_list) == len(get_function_info(self._func)['args'])) if self._func else False:
            raise MXValueError(
                f'Length of argument list must be same with callback function.\n'
                f'given: {len(self._arg_list)}, expected: {len(get_function_info(self._func)["args"])}'
            )

    def __eq__(self, o: 'MXFunction') -> bool:
        instance_check = isinstance(o, MXFunction)
        arg_list_check = o._arg_list == self._arg_list
        return_type_check = o._return_type == self._return_type
        exec_time_check = o._exec_time == self._exec_time
        timeout_check = o._timeout == self._timeout
        range_type_check = o._range_type == self._range_type

        return (
            super().__eq__(o) and instance_check and arg_list_check and return_type_check and exec_time_check and timeout_check and range_type_check
        )

    def __getstate__(self):
        state = super().__getstate__()

        state['_return_type'] = self._return_type
        state['_arg_list'] = self._arg_list
        state['_exec_time'] = self._exec_time
        state['_timeout'] = self._timeout
        state['_range_type'] = self._range_type

        del state['_return_value']
        del state['_running']
        del state['_running_scenario_list']

        return state

    def __setstate__(self, state):
        super().__setstate__(state)

        self._type = state['_type']
        self._min = state['_min']
        self._max = state['_max']
        self._cycle = state['_cycle']
        self._format = state['_format']

        self._return_value = None
        self._running = False
        self._running_scenario_list = []

    async def execute(self, execute_request: Union[MXExecuteRequest, MXInnerExecuteRequest]) -> MXDataType:
        if not isinstance(execute_request, (MXExecuteRequest, MXInnerExecuteRequest)):
            raise MXTypeError(f'[{get_current_function_name()}] Wrong Request type: {type(execute_request)}')

        execute_request.timer_start()

        self._running = True

        execute_msg = execute_request.trigger_msg
        self._running_scenario_list.append(execute_msg.scenario)
        MXLOG_DEBUG(f'[FUNC RUN] run {self._name} function by {execute_msg.scenario}', 'green')

        async def async_wrapper(func: Callable, *args: List[MXDataType]) -> MXDataType:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: func(*args))

        if asyncio.iscoroutinefunction(self._func):
            result = await self._func(*execute_msg.tuple_arguments())
        else:
            result = await async_wrapper(self._func, *execute_msg.tuple_arguments())

        return result

    def dict(self) -> dict:
        return {
            'name': self._name,
            'category': (
                (self._category.function_id if issubclass(self._category, SkillFunction) else self._category.value_id) if self._category else None
            ),
            'description': self._desc,
            'exec_time': self._exec_time * 1000 if self._exec_time is not None else 0,
            'return_type': self._return_type.value,
            'energy': self._energy,
            'tags': [tag.dict() for tag in self._tag_list],
            'use_arg': True if len(self._arg_list) > False else False,
            'arguments': [argument.dict() for argument in self._arg_list] if self._arg_list else [],
        }

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    def add_value_to_update(
        self,
        value: MXValue,
        update_value_to: MXDataType = None,
        callback: Optional[Callable[..., Any] | Callable[..., Coroutine[Any, Any, MXDataType]]] = None,
    ) -> None:
        async def async_update_value_to_callback(set_value: MXDataType = None) -> MXDataType | None:
            new_value = await value.async_update(set_value=set_value)
            return new_value

        def create_task_with_set_value(arguments: List[MXArgumentData] = None) -> asyncio.Task:
            return asyncio.create_task(async_update_value_to_callback(set_value=update_value_to))

        def create_task_without_set_value(arguments: List[MXArgumentData] = None) -> asyncio.Task:
            return asyncio.create_task(async_update_value_to_callback())

        def create_task_with_callback(arguments: List[MXArgumentData] = None) -> asyncio.Task:
            return asyncio.create_task(callback(arguments=arguments))

        if not isinstance(value, MXValue):
            raise MXTypeError(f'value must be MXValue object')

        if update_value_to:
            value_update_callback = create_task_with_set_value
        else:
            if not callback:
                value_update_callback = create_task_without_set_value
            elif asyncio.iscoroutinefunction(callback):
                value_update_callback = create_task_with_callback
            else:
                value_update_callback = callback

        self._value_update_map[value.name] = dict(
            value=value,
            callback=value_update_callback,
        )

    def generate_execute_result_message(
        self,
        execute_request: Union[MXExecuteRequest, MXInnerExecuteRequest],
    ) -> MXExecuteResultMessage:
        trigger_msg = execute_request.trigger_msg
        result_msg = execute_request.result_msg

        if isinstance(result_msg.return_value, BinaryBase64):
            return_value = str(result_msg.return_value)
        else:
            return_value = result_msg.return_value

        return MXExecuteResultMessage(
            function_name=trigger_msg.function_name,
            thing_name=result_msg.thing_name,
            middleware_name=result_msg.middleware_name,
            scenario=trigger_msg.scenario,
            client_id=trigger_msg.client_id,
            request_ID=trigger_msg.request_ID,
            return_type=result_msg.return_type,
            return_value=return_value,
            error=result_msg.error,
            action_type=execute_request.action_type,
        )

    def get_argument(self, name: str) -> MXArgument:
        for arg in self._arg_list:
            if arg.name == name:
                return arg
        return None

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
    def exec_time(self) -> float:
        return self._exec_time

    @property
    def timeout(self) -> float:
        return self._timeout

    @property
    def arg_list(self) -> List[MXArgument]:
        return self._arg_list

    @property
    def return_type(self) -> MXType:
        return self._return_type

    @property
    def return_value(self) -> MXDataType:
        return self._return_value

    @property
    def running(self) -> bool:
        return self._running

    @property
    def range_type(self) -> MXRangeType:
        return self._range_type

    @property
    def running_scenario_list(self) -> List[str]:
        return self._running_scenario_list

    # ==================================
    #             _    _
    #            | |  | |
    #  ___   ___ | |_ | |_   ___  _ __
    # / __| / _ \| __|| __| / _ \| '__|
    # \__ \|  __/| |_ | |_ |  __/| |
    # |___/ \___| \__| \__| \___||_|
    # ==================================

    @exec_time.setter
    def exec_time(self, exec_time: float) -> None:
        self._exec_time = exec_time

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        self._timeout = timeout

    @arg_list.setter
    def arg_list(self, arg_list: List[MXArgument]) -> None:
        self._arg_list = arg_list

    @return_type.setter
    def return_type(self, return_type: MXType) -> None:
        self._return_type = return_type

    @return_value.setter
    def return_value(self, return_value: MXDataType) -> None:
        self._return_value = return_value

    @running.setter
    def running(self, running: bool) -> None:
        self._running = running

    @range_type.setter
    def range_type(self, range_type: MXRangeType) -> None:
        self._range_type = range_type


if __name__ == '__main__':
    pass
