from big_thing_py.utils.log_util import *
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore
from enum import Enum
from typing import Optional, Dict, Tuple, Any

from dataclasses import dataclass

# Suppress only the single InsecureRequestWarning from urllib3 needed
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class RequestMethod(Enum):
    GET = 'GET'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


@dataclass
class RequestResponse:
    ok: bool
    reason: str
    status_code: int
    json: dict = None
    text: str = None
    exception: Exception = Exception()


def api_request(
    method: RequestMethod,
    url: str,
    query: Dict[str, Any] = None,
    data: Dict[str, Any] = None,
    headers: Dict[str, Any] = None,
    json: Dict[str, Any] = None,
    auth: Tuple[str, str] = None,
    verify: bool = False,
    allow_redirects: bool = True,
    timeout: float = None,
    retries: int = 3,
) -> Optional[RequestResponse]:
    headers = headers or {}
    request_response = RequestResponse(ok=False, reason='', status_code=0, json=None, text=None)

    for attempt in range(retries):
        try:
            response = requests.request(
                method=method.value,
                url=url,
                params=query,
                data=data,
                headers=headers,
                json=json,
                auth=auth,
                verify=verify,
                allow_redirects=allow_redirects,
                timeout=(1, timeout) if timeout else None,
            )

            ok = response.ok
            reason = response.reason
            status_code = response.status_code
            try:
                json_string = response.json()
            except Exception as e:
                json_string = None
            text = response.text

            try:
                request_response = RequestResponse(ok=ok, reason=reason, status_code=status_code, json=json_string, text=text)
            except Exception as e:
                request_response = RequestResponse(ok=ok, reason=reason, status_code=status_code, json=json_string, text=text)

            if ok:
                return request_response
            else:
                MXLOG_ERROR(f'Response validation failed, Status Code: {response.status_code}. Reason: {response.reason}, Attempt: {attempt + 1}')
        except requests.exceptions.RequestException as e:
            request_response.exception = e
            MXLOG_WARN(f'Failed to request API: {e}. Attempt: {attempt + 1}')
    else:
        MXLOG_ERROR('All API requests failed after retries.')
        return request_response


if __name__ == '__main__':
    response = api_request('https://www.google.com')
    print(response)
