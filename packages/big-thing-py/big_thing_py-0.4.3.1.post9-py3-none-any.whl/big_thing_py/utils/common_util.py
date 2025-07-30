from big_thing_py.common import *
from big_thing_py.utils.exception_util import *

import inspect
import socket
import json
import time
from datetime import datetime
import platform
import os
import copy
import random
import toml
from pathlib import Path
import getmac
import subprocess
import re
import sys
import typing
import importlib.metadata
import functools
from termcolor import cprint


def static_vars(**kwargs) -> Callable:
    def decorator(func):
        for k, v in kwargs.items():
            setattr(func, k, v)

        @functools.wraps(func)
        def wrapper(*args, **kwds):
            return func(*args, **kwds)

        return wrapper

    return decorator


def get_type_name(typ: typing.Type) -> str:
    origin = typing.get_origin(typ)
    if origin is None:
        return typ.__name__
    args = typing.get_args(typ)
    args_str = ", ".join(get_type_name(arg) for arg in args)
    return f"{origin.__name__}[{args_str}]"


def get_function_info(func: Callable) -> Dict[str, Union[str, List[Tuple[str, Any]]]]:
    sig = inspect.signature(func)
    params = [(param.name, param.annotation) for param in sig.parameters.values()]
    ret_type = sig.return_annotation
    if not ret_type is None:
        if isinstance(ret_type, str):
            try:
                ret_type = eval(ret_type)
            except NameError:
                pass
        ret_type = get_type_name(ret_type)
    return dict(name=func.__name__, args=params, return_type=ret_type)


def get_current_function_name() -> str:
    frame = inspect.currentframe().f_back
    while frame:
        func = frame.f_globals.get(frame.f_code.co_name)
        if func and hasattr(func, '__wrapped__'):
            return func.__wrapped__.__name__
        elif not frame.f_code.co_name.startswith('<'):
            return frame.f_code.co_name
        frame = frame.f_back
    raise RuntimeError("Unable to find valid function name")


def get_upper_function_name(depth: int = 1, frame=None) -> str:
    if frame is None:
        frame = inspect.stack()[1].frame
    if depth == 1:
        co_name = frame.f_back.f_code.co_name
    elif depth > 1:
        co_name = get_upper_function_name(depth - 1, frame.f_back)
    else:
        co_name = 'too many steps... return MAX upper function name'
    return co_name


def get_upper_function(depth: int = 2) -> Optional[Callable]:
    """
    현재 함수를 호출한 상위 함수 객체를 찾습니다.

    :param depth: 탐색할 프레임 깊이 (기본값 2)
                  - 1: 바로 상위 프레임
                  - 2: 두 단계 상위 프레임
                  - N: N단계 상위 프레임
    """
    current_frame = inspect.currentframe()
    if not current_frame:
        return None

    # 지정된 depth만큼 프레임 이동
    target_frame = current_frame
    for _ in range(depth):
        target_frame = target_frame.f_back
        if not target_frame:
            return None

    # 호출자 함수 이름 추출
    caller_name = target_frame.f_code.co_name

    # 1. 지역 변수에서 조회 (중첩 함수/클래스 메서드)
    caller_func = target_frame.f_locals.get(caller_name)

    # 2. 전역 변수에서 조회 (일반 함수)
    if caller_func is None:
        caller_func = target_frame.f_globals.get(caller_name)

    # 3. 클래스 인스턴스 메서드인 경우
    if caller_func is None and 'self' in target_frame.f_locals:
        instance = target_frame.f_locals['self']
        caller_func = getattr(instance, caller_name, None)

    return caller_func


def get_function_return_type(func: Callable, to_mxtype: bool = True) -> Union[MXType, str]:
    return_type = inspect.signature(func).return_annotation
    if return_type is inspect.Signature.empty:
        raise MXNotSupportedError('Return type is not defined!!!')

    if to_mxtype:
        return MXType.get(return_type)
    else:
        return return_type


def get_mac_address(ble: bool = True) -> str:
    if ble:
        mac_address = get_ble_mac_address()
    else:
        mac_address = get_wifi_mac_address()

    if mac_address:
        mac_address = mac_address.replace(':', '').upper()
        return mac_address
    else:
        return None


def get_wifi_mac_address() -> str:
    mac_address = getmac.get_mac_address()
    return mac_address


def get_ble_mac_address() -> str:
    try:
        output = subprocess.check_output(['hciconfig']).decode('utf-8')
        matches = re.findall(r'BD Address: ([0-9A-F:]+)', output)
        if matches:
            return matches[0]
        else:
            return None
    except Exception as e:
        print("에러 발생: ", e)
        return None


def transform_mac_address(mac_address: str, to_colon: bool = True) -> str:
    if to_colon:
        return ':'.join(mac_address[i : i + 2] for i in range(0, len(mac_address), 2))
    else:
        return mac_address.replace(':', '')


def get_current_datetime(mode: TimeFormat = TimeFormat.UNIXTIME) -> Union[str, float]:
    now = datetime.now()

    if mode == TimeFormat.DATETIME1:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif mode == TimeFormat.DATETIME2:
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")
    elif mode == TimeFormat.DATETIME3:
        return now.strftime("%Y%m%d_%H%M%S")
    elif mode == TimeFormat.DATE:
        return now.strftime("%Y-%m-%d")
    elif mode == TimeFormat.TIME:
        return now.strftime("%H:%M:%S")
    elif mode == TimeFormat.UNIXTIME:
        return time.time()

    return time.time()


def type_converter(in_type: Union[MXType, type, str, None]) -> Union[type, MXType]:
    if type(in_type) == MXType:
        if in_type in (MXType.BINARY, MXType.STRING):
            return str
        elif in_type == MXType.BOOL:
            return bool
        elif in_type == MXType.DOUBLE:
            return float
        elif in_type == MXType.INTEGER:
            return int
        elif in_type in (MXType.VOID, MXType.UNDEFINED):
            return None
        else:
            raise MXNotSupportedError('Unexpected python type!!!')
    elif type(in_type) == type:
        if in_type == int:
            return MXType.INTEGER
        elif in_type == float:
            return MXType.DOUBLE
        elif in_type == bool:
            return MXType.BOOL
        elif in_type == bytes:
            return MXType.BINARY
        elif in_type == str:
            return MXType.STRING
        elif in_type == type(None):
            return MXType.VOID
        else:
            raise MXNotSupportedError('Unexpected MXType type!!!')
    elif type(in_type) == str:
        if in_type == 'int':
            return MXType.INTEGER
        elif in_type == 'void':
            return MXType.VOID
        elif in_type == 'double':
            return MXType.DOUBLE
        elif in_type == 'bool':
            return MXType.BOOL
        elif in_type == 'binary':
            return MXType.BINARY
        elif in_type == 'string':
            return MXType.STRING
        elif in_type == 'undefined':
            return MXType.UNDEFINED
        else:
            raise MXNotSupportedError('Unexpected MXType type!!!')
    elif in_type == None or type(in_type) == type(None):
        return MXType.VOID


def json_file_read(path: str, mode: str = 'r') -> Union[dict, bool]:
    try:
        with open(path, mode) as f:
            return json.load(f)
    except FileNotFoundError as e:
        return False
    except json.JSONDecodeError as e:
        return False


def json_file_write(path: str, data: Union[str, dict], mode: str = 'w', indent: int = 4, ensure_ascii: bool = True) -> None:
    with open(path, mode) as f:
        if isinstance(data, (dict, str)):
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        else:
            raise Exception(f'common_util.json_file_write: data type error - {type(data)}')


def get_project_root(project_name: str = 'big-thing-py') -> Path:
    start_path = Path(__file__)
    while True:
        if str(start_path).split('/')[-1] == project_name:
            return str(start_path)
        else:
            start_path = start_path.parent


def check_valid_identifier(identifier: str) -> MXErrorCode:
    pattern = r'^[_a-zA-Z가-힣][_a-zA-Z0-9가-힣]*$'

    if len(identifier) >= IDENTIFIER_LIMIT:
        return MXErrorCode.TOO_LONG_IDENTIFIER
    elif not bool(re.match(pattern, identifier)):
        return MXErrorCode.INVALID_DATA
    else:
        return MXErrorCode.NO_ERROR


def convert_special_char(char: str) -> str:
    # conversion_dict = {
    #     ' ': 'space',
    #     '!': 'exclamation_mark',
    #     '"': 'double_quote',
    #     '#': 'hash',
    #     '$': 'dollar',
    #     '%': 'percent',
    #     '&': 'ampersand',
    #     "'": 'single_quote',
    #     '(': 'left_parenthesis',
    #     ')': 'right_parenthesis',
    #     '*': 'asterisk',
    #     '+': 'plus',
    #     ',': 'comma',
    #     '-': 'hyphen',
    #     '.': 'period',
    #     '/': 'slash',
    #     ':': 'colon',
    #     ';': 'semicolon',
    #     '<': 'less_than',
    #     '=': 'equals',
    #     '>': 'greater_than',
    #     '?': 'question_mark',
    #     '@': 'at_sign',
    #     '[': 'left_bracket',
    #     '\\': 'backslash',
    #     ']': 'right_bracket',
    #     '^': 'caret',
    #     '`': 'backtick',
    #     '{': 'left_brace',
    #     '|': 'vertical_bar',
    #     '}': 'right_brace',
    #     '~': 'tilde'
    # }
    conversion_dict = {
        ' ': 'sp',
        '!': 'ex',
        '"': 'dq',
        '#': 'hs',
        '$': 'dl',
        '%': 'pc',
        '&': 'am',
        "'": 'sq',
        '(': 'lp',
        ')': 'rp',
        '*': 'as',
        '+': 'pl',
        ',': 'cm',
        '-': 'mn',
        '.': 'pd',
        '/': 'sl',
        ':': 'cl',
        ';': 'sc',
        '<': 'lt',
        '=': 'eq',
        '>': 'gt',
        '?': 'qm',
        '@': 'at',
        '[': 'lb',
        '\\': 'bs',
        ']': 'rb',
        '^': 'cr',
        '`': 'bt',
        '{': 'lc',
        '|': 'vb',
        '}': 'rc',
        '~': 'td',
    }
    if char in conversion_dict:
        return f'_{conversion_dict[char]}_'
    else:
        return char


def convert_to_valid_string(input_string: str) -> str:
    converted_chars = [convert_special_char(char) for char in input_string]
    return ''.join(converted_chars)


def convert_url_to_ip(url: str) -> str:
    ip_list = url.split(".")
    not_ip = False

    for ip_token in ip_list:
        if not ip_token.isdigit():
            not_ip = True
            break

    if not_ip:
        host_ip = socket.gethostbyname(url.strip())
        return host_ip
    elif not all([(0 <= int(ip_token) <= 255) for ip_token in ip_list]) or len(ip_list) != 4:
        raise Exception('wrong ip format')
    else:
        return url


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('192.168.0.1', 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception as e:
        return f"Error occurred: {e}"


def check_python_version() -> bool:
    if not (sys.version_info[0] >= 3 and sys.version_info[1] > 6):
        return False

    return True


def is_valid_ip_address(ip_address: str) -> bool:
    if ip_address:
        octets = ip_address.split('.')
    else:
        return False

    if len(octets) != 4:
        return False
    for octet in octets:
        try:
            value = int(octet)
        except ValueError:
            return False
        if not 0 <= value <= 255:
            return False
    return True


def is_raspberry_pi() -> bool:
    try:
        with open('/proc/device-tree/model', 'r') as f:
            return 'raspberry pi' in f.read().lower()
    except FileNotFoundError:
        return False


def check_os_architecture() -> str:
    return platform.architecture()[0]


def install_missing_package(error) -> None:
    import subprocess

    package_name = str(error).split("'")[1]
    subprocess.run([sys.executable, "-m", "pip", "install", package_name])


def dummy_func(arg_list: list) -> Callable:
    args = ', '.join([str(arg) for arg in arg_list])
    lambda_str = f"lambda {args}: None"
    exec(lambda_str)
    return eval(lambda_str)


def sdk_version() -> str:
    package_name = __package__.split('.')[0]

    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        try:
            # Locate the project root and read pyproject.toml
            project_root = get_project_root()
            pyproject_path = Path(project_root) / 'pyproject.toml'
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                pyproject_data = toml.load(f)

            # Try to get the version from [tool.poetry] or [project]
            version: str = pyproject_data.get('tool', {}).get('poetry', {}).get('version') or pyproject_data.get('project', {}).get('version')
            pypi_version = version.replace('-', '.post')
            return pypi_version
        except Exception:
            return '0.0.0'


def prune_payload(payload: str, mode: MXPrintMode = MXPrintMode.ABBR) -> str:
    if mode == MXPrintMode.SKIP:
        payload = colored(f'skip... (mode={mode})', 'yellow')
    elif mode == MXPrintMode.ABBR:
        if payload.count('\n') > 10:
            payload = '\n'.join(payload.split('\n')[:10]) + '\n' + colored(f'skip... (mode={mode})', 'yellow')
        elif len(payload) > 1000:
            payload = payload[:1000] + '\n' + colored(f'skip... (mode={mode})', 'yellow')
        else:
            pass
    elif mode == MXPrintMode.FULL:
        pass
    else:
        raise Exception(f'[prune_payload] Unknown mode!!! mode should be [skip|abbr|full] mode : {mode}', 'red')

    return payload


# TODO (thsvkd): Not supported (ENUM, LIST, DICT) MXType yet
def normalize_mx_type(type: MXType) -> MXType:
    if type in [MXType.ENUM, MXType.LIST, MXType.DICT]:
        return MXType.STRING
    else:
        return type


def normalize_bound(type: MXType, bound: Optional[Tuple[Any, Any]] = None) -> Tuple[Any, Any]:
    if type in [MXType.STRING, MXType.BINARY]:
        if bound:
            MXLOG_INFO('`bound` parameter will be ignored because type is STRING or BINARY. set bound to -1, -1')

        return -1, -1
    elif type == MXType.BOOL:
        if bound:
            MXLOG_INFO('`bound` parameter will be ignored because type is BOOL. set bound to 0, 1')

        return 0, 1
    else:
        if not bound:
            raise MXValueError('`bound` must be given when type is not STRING or BINARY')

        return bound


def print_func_info(func) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cprint(f'[print_func_info] function : {func.__name__}', 'green')
        cprint(f'[print_func_info] args     : {args}', 'cyan')
        cprint(f'[print_func_info] kwargs   : {kwargs}', 'magenta')
        return func(*args, **kwargs)

    return wrapper


if __name__ == '__main__':
    pass
