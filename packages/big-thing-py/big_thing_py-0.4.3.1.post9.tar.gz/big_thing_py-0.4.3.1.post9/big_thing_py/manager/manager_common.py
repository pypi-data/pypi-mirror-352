from big_thing_py.utils import *
from big_thing_py.core import MXThing
import functools
import asyncio


class ThingNameRawIDConvertMode:
    ThingNameToRawDeviceID = 0
    RawDeviceIDToThingName = 1


def list_arg_to_str(list_arg: List[MXDataType]) -> str:
    formatted_list = []
    for x in list_arg:
        if isinstance(x, bool):
            formatted_list.append(str(x))
        elif isinstance(x, float):
            formatted_list.append(f"{x:.4f}")
        elif isinstance(x, (int, str)):
            formatted_list.append(str(x))
        else:
            raise ValueError(f"Unsupported type: {type(x)}")
    return '|'.join(formatted_list)


def generate_enum_list_str(list_str: List[str]) -> str:
    return '|'.join(list_str)


def print_method_info(func: Callable) -> None:
    @functools.wraps(func)
    async def async_wrapper(self: MXThing, *args, **kwargs):
        MXLOG_DEBUG(f'{func.__name__} at {self._name} actuate!!!', 'green')
        ret = await func(self, *args, **kwargs)
        return ret

    @functools.wraps(func)
    def sync_wrapper(self: MXThing, *args, **kwargs):
        MXLOG_DEBUG(f'{func.__name__} at {self._name} actuate!!!', 'green')
        ret = func(self, *args, **kwargs)
        return ret

    if asyncio.iscoroutinefunction(func):
        async_wrapper.is_decorated = True
        return async_wrapper
    else:
        sync_wrapper.is_decorated = True
        return sync_wrapper


def set_inner_value_buffer(inner_value_buffer: str, target_value: Any = None):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(self: MXThing, *args, **kwargs):
            result = await func(self, *args, **kwargs)

            if not target_value is None:
                setattr(self, inner_value_buffer, target_value)
            else:
                setattr(self, inner_value_buffer, result)
            MXLOG_DEBUG(f'Setting inner value buffer {inner_value_buffer} to {result}.', 'magenta')
            return result

        @functools.wraps(func)
        def sync_wrapper(self: MXThing, *args, **kwargs):
            result = func(self, *args, **kwargs)

            if not target_value is None:
                setattr(self, inner_value_buffer, target_value)
            else:
                setattr(self, inner_value_buffer, result)
            MXLOG_DEBUG(f'Setting inner value buffer {inner_value_buffer} to {result}.', 'magenta')
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def skip_func_execute_if(
    inner_value_buffer: Union[str, List[str]],
    default_return_value: Any = True,
    target_value: Any = None,
    target_argument: Union[str, List[str]] = None,
):
    """
    Decorator to skip the function execution based on the class attribute or function arguments.

    Parameters:
    inner_value_buffer (Union[str, List[str]]): The class attribute name or a list of attribute names.
    target_value (Any): The value to compare with the class attribute(s) or function arguments.
    target_argument_name_list (List[str]): The list of function argument names to compare with the target_value.

    Raises:
    ValueError: If the lengths of inner_value_buffer and target_argument_name_list do not match when inner_value_buffer is a list.
                If target_value is None when inner_value_buffer is not a list.
    """

    def decorator(func):
        @functools.wraps(func)
        def base_wrapper(self, *args, **kwargs) -> bool:
            skip_func_run = True
            inner_value_buffer_instance = getattr(self, inner_value_buffer)

            if isinstance(inner_value_buffer, list):
                if target_argument is None or not isinstance(target_argument, list) or len(inner_value_buffer_instance) != len(target_argument):
                    raise ValueError('The lengths of inner_value_buffer and target_argument_name_list do not match.')

                arg_names = [arg_name for arg_name in func.__code__.co_varnames[1 : func.__code__.co_argcount]]
                target_args = [args[i] for i, _ in enumerate(arg_names)]
                for inner_value, target_arg_value in zip(inner_value_buffer_instance, target_args):
                    if inner_value == target_arg_value:
                        skip_func_run = True
                    else:
                        skip_func_run = False
                        break
            else:
                if not target_value is None and target_argument is None:
                    if inner_value_buffer_instance == target_value:
                        skip_func_run = True
                    else:
                        skip_func_run = False
                elif target_value is None and not target_argument is None:
                    if isinstance(target_argument, list):
                        if not isinstance(inner_value_buffer_instance, list) or len(inner_value_buffer_instance) != len(target_argument):
                            raise ValueError('The lengths of inner_value_buffer and target_argument_name_list do not match.')

                        arg_names = [arg_name for arg_name in func.__code__.co_varnames[1 : func.__code__.co_argcount]]
                        target_args = [args[i] for i, _ in enumerate(arg_names)]
                    elif isinstance(target_argument, str):
                        inner_value_buffer_instance = [inner_value_buffer_instance]
                        target_args = args
                    else:
                        raise ValueError('target_argument_name_list must be a list or a string.')

                    for inner_value, target_arg_value in zip(inner_value_buffer_instance, target_args):
                        if inner_value == target_arg_value:
                            skip_func_run = True
                        else:
                            skip_func_run = False
                            break
                else:
                    raise ValueError('target_value cannot be None when inner_value_buffer is not a list.')

            return skip_func_run
            # if skip_func_run:
            #     MXLOG_DEBUG(f'Skipping function {func.__name__} as the condition is met.', 'yellow')
            #     return default_return_value
            # else:
            #     return func(self, *args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            skip_func_run = base_wrapper(self, *args, **kwargs)
            if skip_func_run:
                MXLOG_DEBUG(f'Skipping function {func.__name__} as the condition is met.', 'yellow')
                return default_return_value
            else:
                return await func(self, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            skip_func_run = base_wrapper(self, *args, **kwargs)
            if skip_func_run:
                MXLOG_DEBUG(f'Skipping function {func.__name__} as the condition is met.', 'yellow')
                return default_return_value
            else:
                return func(self, *args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def find_class_in_hierarchy(instance, target_class) -> bool:
    current_class = type(instance)

    while current_class is not object:
        if issubclass(current_class, target_class):
            return True
        current_class = current_class.__base__

    return False


def thing_name_uid_convert(input: str, mode: ThingNameRawIDConvertMode) -> str:
    # Real device id -> thing name
    if mode == ThingNameRawIDConvertMode.RawDeviceIDToThingName:
        uid = input

        if ':' in input:
            convert_str = transform_mac_address(uid, to_colon=False)
        elif '-' in uid:
            convert_str = input.replace('-', '_')
        else:
            convert_str = uid
    # thing name -> real device id
    elif mode == ThingNameRawIDConvertMode.ThingNameToRawDeviceID:
        thing_name = input
        category = thing_name.split('__')[0]
        uid = thing_name.split('__')[1]

        if len(uid) == 12 and uid.isupper():
            convert_str = transform_mac_address(uid, to_colon=True)
        elif '_' in uid:
            convert_str = uid.replace('_', '-')
        else:
            convert_str = uid
    else:
        convert_str = input

    return convert_str


def value_update_callback(func):
    @functools.wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        arguments = kwargs['arguments']
        ret = await func(self, arguments, *args, **kwargs)
        return ret

    @functools.wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        arguments = kwargs['arguments']
        ret = func(self, arguments, *args, **kwargs)
        return ret

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
