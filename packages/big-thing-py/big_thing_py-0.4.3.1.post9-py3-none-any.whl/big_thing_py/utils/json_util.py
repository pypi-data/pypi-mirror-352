from big_thing_py.common import *
from big_thing_py.utils.log_util import *
from big_thing_py.utils.exception_util import *

import json
from jsonschema import validate, ValidationError


def json_string_to_dict(json_string: str) -> Union[str, dict, list]:
    try:
        if type(json_string) not in [str, bytes]:
            raise json.JSONDecodeError('input string must be str, bytes type.', json_string, 0)
        else:
            return json.loads(json_string)

    except json.JSONDecodeError as e:
        MXLOG_DEBUG(f'[json_string_to_dict] input string must be json format string. return raw object... ', 'red')
        print_error(e)
        return json_string


def dict_to_json_string(
    dict_object: Union[dict, list, str],
    ensure_ascii: bool = True,
    pretty: bool = True,
    indent: int = 4,
    default: Callable = str,
) -> Union[str, bool]:
    try:
        if type(dict_object) == dict:
            if pretty:
                return json.dumps(dict_object, ensure_ascii=ensure_ascii, sort_keys=True, indent=indent, default=default)
            else:
                return json.dumps(dict_object, ensure_ascii=ensure_ascii, default=default)
        elif type(dict_object) == list:
            if pretty:
                return '\n'.join([json.dumps(item, ensure_ascii=ensure_ascii, sort_keys=True, indent=indent) for item in dict_object])
            else:
                return '\n'.join([json.dumps(item, ensure_ascii=ensure_ascii) for item in dict_object])
        else:
            if pretty:
                json.dumps(json.loads(dict_object), ensure_ascii=ensure_ascii, sort_keys=True, indent=indent, default=default)
            else:
                return str(dict_object)
    except Exception as e:
        MXLOG_DEBUG(f'[dict_to_json_string] input object must be dict or list or str. return False... ', 'red')
        print_error(e)
        return False


def extract_json_schema_data(raw_data: Dict[Any, Any], schema: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
    try:
        validate(instance=raw_data, schema=schema)
        processed_data = {key: raw_data[key] for key in schema['properties'].keys() if key in raw_data}

        return processed_data
    except ValidationError as e:
        print(f"Data validation failed: {e.message}")
        return None
    except KeyError as e:
        print(f"Missing required field: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None
