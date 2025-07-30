from big_thing_py.utils import *
from big_thing_py.core.argument import MXArgument
from big_thing_py.big_thing import *
from big_thing_py.super.super_request import *

from .const import *
from ...common.helper.util import *
from ...common.helper.const import *

import functools
from dataclasses import dataclass, asdict, field
from typing import TypedDict, TYPE_CHECKING
from itertools import chain

if TYPE_CHECKING:
    from big_thing_py.super import MXSuperFunction, MXSuperExecuteRequest


class HierarchicalServiceTable(TypedDict):
    hierarchy: str
    values: List[MXValue]
    functions: List[MXFunction]


@dataclass
class MXCallLineInfo:
    subservice: str  # St
    tag_list: Union[List[Union[MXTag, str]], Tuple[Union[MXTag, str], ...]]
    arg_list: Union[Tuple[MXArgument], Tuple]
    return_type: MXType
    service_type: MXServiceType
    range_type: MXRangeType
    line_num: int = -1

    def __post_init__(self):
        if isinstance(self.tag_list, list):
            tag_list = tuple(self.tag_list)
            object.__setattr__(self, 'tag_list', tag_list)

        processed_tags = tuple(tag.name if isinstance(tag, MXTag) else tag for tag in self.tag_list)
        object.__setattr__(self, 'tag_list', processed_tags)

    def __eq__(self, o: Optional['MXCallLineInfo']) -> bool:
        # exclude the comparison of arg_list
        return (
            self.subservice == o.subservice
            and self.tag_list == o.tag_list
            and self.return_type == o.return_type
            and self.service_type == o.service_type
            and self.range_type == o.range_type
        )

    def __str__(self) -> str:
        tag_list_str = ' '.join([f'#{tag}' for tag in self.tag_list])
        range_type_str = 'all' if self.range_type == MXRangeType.ALL else ''
        return f'({range_type_str}{tag_list_str}).{self.subservice}'


@dataclass(frozen=True)
class MXCallRequester:
    middleware: str  # MWr
    scenario: str  # Scr

    def __str__(self):
        return f'{self.middleware}/{self.scenario}'


@dataclass(frozen=True)
class MXScheduleTarget:
    subservice: str  # St
    middleware: str  # MWt
    tag_list: Union[List[Union[MXTag, str]], Tuple[Union[MXTag, str], ...]] = field(default_factory=tuple)
    range_type: MXRangeType = field(default=MXRangeType.UNDEFINED)

    def __post_init__(self):
        if isinstance(self.tag_list, list):
            tag_list = tuple(self.tag_list)
            object.__setattr__(self, 'tag_list', tag_list)

        processed_tags = tuple(tag.name if isinstance(tag, MXTag) else tag for tag in self.tag_list)
        object.__setattr__(self, 'tag_list', processed_tags)

    def __eq__(self, o: Optional['MXScheduleTarget']) -> bool:
        return self.subservice == o.subservice and self.middleware == o.middleware

    # subservice, middleware만 같으면 dict에서 key로 사용될 수 있도록 하기위해 재정의
    def __hash__(self) -> int:
        return hash((self.subservice, self.middleware))

    def __str__(self) -> str:
        tag_list_str = ' '.join([f'#{tag}' for tag in self.tag_list])
        range_type_str = 'all' if self.range_type == MXRangeType.ALL else ''
        return f'{range_type_str}({tag_list_str}).{self.subservice} at {self.middleware}'


@dataclass(frozen=True)
class MXExecuteTarget:
    subservice: str  # St
    middleware: str  # MWt
    thing: str  # Tht

    def __str__(self) -> str:
        return f'{self.subservice} at {self.middleware}/{self.thing}'


def track_calls(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        return await _track_calls_impl(func, *args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        return _track_calls_impl(func, *args, **kwargs)

    async def _async_inner_wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    def _sync_inner_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # 비동기 함수 여부에 따라 적절한 래퍼 선택
    if inspect.iscoroutinefunction(func):
        async_wrapper._original = _async_inner_wrapper
        return async_wrapper
    else:
        sync_wrapper._original = _sync_inner_wrapper
        return sync_wrapper


async def _track_calls_impl(func, *args, **kwargs):
    caller_func = get_upper_function(depth=3)

    if 'arg_list' not in kwargs:
        kwargs['arg_list'] = []
    kwargs = asdict(verify_call_line_info_arguments(**kwargs))

    if hasattr(caller_func, DRY_RUN_ATTRIBUTE):
        if not hasattr(caller_func, CALL_LINE_INFO_LIST_ATTRIBUTE):
            setattr(caller_func, CALL_LINE_INFO_LIST_ATTRIBUTE, [])

        call_line_info_list: list = getattr(caller_func, CALL_LINE_INFO_LIST_ATTRIBUTE)
        call_line_info = MXCallLineInfo(**kwargs)
        MXLOG_DEBUG(TAB + f'<{call_line_info}>', 'green')
        call_line_info_list.append(call_line_info)
    elif hasattr(caller_func, LINE_NUM_ATTRIBUTE):
        if LINE_NUM_ATTRIBUTE in kwargs:
            kwargs.pop(LINE_NUM_ATTRIBUTE)

        if inspect.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        caller_func.line_num += 1
        return result
    else:
        raise MXInvalidRequestError(f'Invalid function state for {caller_func.__name__}')


def verify_call_line_info_arguments(
    subservice: str,
    tag_list: List[str | MXTag],
    arg_list: List[MXArgument | MXDataType],
    return_type: MXType,
    service_type: MXServiceType,
    range_type: MXRangeType,
) -> MXCallLineInfo:
    # Check if the subservice_name is not empty
    if not subservice:
        raise MXValueError(f'subservice_name must be not empty')

    # Check if the tag_list is not empty and all elements are strings
    if not tag_list or len(tag_list) == 0:
        raise MXValueError(f'tag_list must be not empty')
    if not all([isinstance(tag, str) for tag in tag_list]):
        raise MXValueError(f'tag in tag_list must be not empty string')

    # Check if the arg_list is not empty and all elements are MXDataType
    if not all([isinstance(arg, get_args(MXDataType)) for arg in arg_list if not isinstance(arg, MXArgument)]):
        raise MXTypeError(f'arg_list must be a list of MXArgument')

    # Check if the service_type is valid
    if not service_type in [MXServiceType.VALUE, MXServiceType.FUNCTION]:
        raise MXTypeError(f'Invalid service_type: {service_type}')
    elif service_type == MXServiceType.VALUE and return_type == MXType.VOID:
        raise MXTypeError(f'Value service cannot have a return_type of void')

    # Check if the return_type is valid
    if not return_type in [MXType.INTEGER, MXType.DOUBLE, MXType.STRING, MXType.BOOL, MXType.BINARY, MXType.VOID]:
        raise MXTypeError(f'Invalid return_type: {return_type}')

    # Check if the range_type is valid
    if not range_type in [MXRangeType.SINGLE, MXRangeType.ALL]:
        raise MXTypeError(f'Invalid range_type: {range_type}')

    ############################################################

    # Convert tag of type [str] to [MXTag]
    tag_list = [MXTag(str_tag) for str_tag in tag_list if isinstance(str_tag, str)]

    if service_type == MXServiceType.VALUE:
        subservice = f'__{subservice}'
    elif service_type == MXServiceType.FUNCTION:
        subservice = subservice

    return MXCallLineInfo(
        subservice=subservice,
        tag_list=tag_list,
        arg_list=arg_list,
        return_type=return_type,
        service_type=service_type,
        range_type=range_type,
    )


@track_calls
async def call(
    subservice: str,
    tag_list: List[str | MXTag],
    arg_list: Union[Tuple[MXArgument], Tuple] = list(),
    return_type: MXType = MXType.UNDEFINED,
    service_type: MXServiceType = MXServiceType.FUNCTION,
    range_type: MXRangeType = MXRangeType.SINGLE,
) -> List[MXDataType]:
    # from big_thing_py.super import MXSuperFunction, MXSuperExecuteRequest

    super_function_callback = get_upper_function(depth=4)
    target_super_function: MXSuperFunction = super_function_callback.self
    super_execute_request: MXSuperExecuteRequest = super_function_callback.super_execute_request
    call_line_info_list: List[MXCallLineInfo] = super_function_callback.call_line_info_list
    line_num: int = target_super_function.func.line_num

    if not compare_arg_list(target_super_function.arg_list, list(super_execute_request.trigger_msg.tuple_arguments())):
        MXLOG_DEBUG(f'Not matched arg_list')
        return []

    call_line_info = call_line_info_list[line_num]
    result = await target_super_function._create_call_line_execute_task(
        target_super_function=target_super_function,
        call_line_info=call_line_info,
        super_execute_request=super_execute_request,
    )

    return result


# TODO: implement this
def r(line: str = None, *arg_list) -> Union[List[dict], bool]:
    super_service_name = get_upper_function_name()

    range_type = 'all' if 'all' in line else 'single'
    function_name = line.split('.')[1][0 : line.split('.')[1].find('(')]
    bracket_parse: List[str] = re.findall(r'\(.*?\)', line)
    tags = [tag[1:] for tag in bracket_parse[0][1:-1].split(' ')]

    arguments = []
    for bracket_inner_element in bracket_parse[1][1:-1].split(','):
        bracket_inner_element = bracket_inner_element.strip(' ')
        if bracket_inner_element == '':
            continue
        else:
            arguments.append(bracket_inner_element)

    for i, arg in enumerate(arguments):
        if '$' in arg:
            index = int(arg[1:])
            arguments[i] = arg_list[index - 1]

    arguments = tuple(arguments)


def get_candidate_list(
    call_line_info: MXCallLineInfo,
    hierarchical_service_table: Dict[str, HierarchicalServiceTable],
    action_type: MXActionType,
) -> List[MXScheduleTarget | MXExecuteTarget]:
    candidate_target_list: List[MXScheduleTarget | MXExecuteTarget] = []
    subservice = call_line_info.subservice
    for middleware_name, service_list in hierarchical_service_table.items():
        value_list = service_list['values']
        function_list = service_list['functions']
        value_name_list = ['__' + v.name for v in service_list['values']]
        function_name_list = [f.name for f in service_list['functions']]

        combine_list = value_list + function_list
        combine_name_list = value_name_list + function_name_list
        for i, subservice in enumerate(combine_name_list):
            if subservice == call_line_info.subservice:
                if action_type == MXActionType.SUB_SCHEDULE:
                    candidate_target = MXScheduleTarget(
                        subservice=subservice,
                        middleware=middleware_name,
                        tag_list=call_line_info.tag_list,
                        range_type=call_line_info.range_type,
                    )
                else:
                    candidate_target = MXExecuteTarget(
                        subservice=subservice,
                        middleware=middleware_name,
                        thing=combine_list[i].thing_name,
                    )
                candidate_target_list.append(candidate_target)
    else:
        if len(candidate_target_list) == 0:
            MXLOG_ERROR(f'Subservice {subservice} is not exist in hierarchical service list')

    candidate_target_list = list(set(candidate_target_list))
    return candidate_target_list


# def get_call_line_info_list_without_duplicated(call_line_info_list: List[MXCallLineInfo]) -> List[MXCallLineInfo]:
#     seen = []
#     call_line_info_list_without_duplicated = [x for x in call_line_info_list if not (x in seen or seen.append(x))]

#     return call_line_info_list_without_duplicated


def is_candidate_target_empty(candidate_table: Dict[str, List[MXScheduleTarget | MXExecuteTarget]]) -> bool:
    flatten_candidate_target_list = list(chain.from_iterable(candidate_table.values()))
    return len(flatten_candidate_target_list) == 0


def make_request_ID(requester_middleware_name: str, super_thing_name: str, super_service_name: str, line_num: int, execute_order: int = None) -> str:
    return '@'.join(
        [
            requester_middleware_name,
            super_thing_name,
            super_service_name,
            str(line_num) if execute_order is None else f'{str(line_num)}-{str(execute_order)}',
        ]
    )
