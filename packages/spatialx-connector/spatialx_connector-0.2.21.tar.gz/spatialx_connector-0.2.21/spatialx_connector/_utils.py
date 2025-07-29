import sys
import time
import logging
import functools
from enum import Enum
from typing import Optional

import requests
import msgpack
from requests.adapters import Retry
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth

from ._constants import ConnectorKeys


TAB_STRING: str = " " * 4


DEFAULT_LOGGER = logging.getLogger("spatialx_sdks_stdout")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    fmt="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
DEFAULT_LOGGER.addHandler(handler)
DEFAULT_LOGGER.setLevel(logging.INFO)


def time_cache(max_age, maxsize=128, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.

    Args:
        max_age: Time to live for cached results (in seconds).
        maxsize: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """
    def _decorator(fn):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / max_age))

        return _wrapped

    return _decorator


class RequestMode:
    POST: str = "post"
    PUT: str = "put"
    GET: str = "get"


def create_requests_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.1
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


def parse_enum_to_value(data):
    if isinstance(data, list) or isinstance(data, tuple):
        return parse_list_enum_to_value(data)
    if isinstance(data, dict):
        return parse_dict_enum_to_value(data)
    return data.value if isinstance(data, Enum) else data


def parse_list_enum_to_value(data: list):
    return [parse_enum_to_value(v) for v in data]


def parse_dict_enum_to_value(data: dict):
    return {parse_enum_to_value(k): parse_enum_to_value(v) for k, v in data.items()}


def request(
    url: str,
    params={},
    data={},
    json={},
    headers={},
    files={},
    mode: str = RequestMode.POST,
    verify: bool = False,
    authentication: Optional[HTTPBasicAuth] = None,
):
    session = create_requests_session()
    r: requests.Response = getattr(session, mode)(
        url,
        params=parse_enum_to_value(params),
        json=parse_enum_to_value(json),
        data=parse_enum_to_value(data),
        headers=parse_enum_to_value(headers),
        files=parse_enum_to_value(files),
        verify=verify,
        timeout=1800,
        auth=authentication,
    )

    if r.status_code >= 400:
        raise Exception(
            f"Call request to {url} failed with status code {r.status_code}, response {r.text}"
        )
    try:
        response = r.json()
    except:
        try:
            response = msgpack.unpackb(r._content)
        except:
            response = r.text
    r.close()
    return response


def parse_to_str(data, tab_level: int = 0) -> str:
    if isinstance(data, list):
        return list_to_str(data, tab_level)
    if isinstance(data, tuple):
        return tuple_to_str(data, tab_level)
    if isinstance(data, dict):
        return dict_to_str(data, tab_level)
    return f"{data}"


def list_to_str(data: list, tab_level: int = 0) -> str:
    if len(data) == 0:
        return "[""]"
    return "[\n" + "".join([
        TAB_STRING * (tab_level + 1) +
        f"{parse_to_str(value, tab_level + 1)}\n" for value in data
    ]) + TAB_STRING * tab_level + "]"


def tuple_to_str(data: list, tab_level: int = 0) -> str:
    if len(data) == 0:
        return "("")"
    return "(\n" + "".join([
        TAB_STRING * (tab_level + 1) +
        f"{parse_to_str(value, tab_level + 1)}\n" for value in data
    ]) + TAB_STRING * tab_level + ")"


def dict_to_str(data: dict, tab_level: int = 0) -> str:
    if len(data) == 0:
        return "{""}"
    return "{\n" + "".join([
        f"{TAB_STRING * (tab_level + 1)}{key}: "
        f"{parse_to_str(value, tab_level + 1)}\n"
        for key, value in data.items()
    ]) + TAB_STRING * tab_level + "}"


def format_print(data):
    print(parse_to_str(data))


def get_chunk_size(chunk_size: int, file_size: int) -> int:
    if chunk_size > 0:
        if chunk_size > ConnectorKeys.UPLOAD_CHUNK_LARGE_SIZE.value:
            chunk_size = ConnectorKeys.UPLOAD_CHUNK_LARGE_SIZE.value
        return chunk_size

    if file_size < 15*1024*1024:
        return ConnectorKeys.UPLOAD_CHUNK_SMALL_SIZE.value
    elif file_size < 100*1024*1024:
        return ConnectorKeys.UPLOAD_CHUNK_MEDIUM_SIZE.value
    elif file_size < 1024*1024*1024:
        return ConnectorKeys.UPLOAD_CHUNK_NORMAL_SIZE.value

    return ConnectorKeys.UPLOAD_CHUNK_LARGE_SIZE.value


def right_aligning(value: str, length: int, char: str = " "):
    value = str(value)
    length = max(length, len(value))
    return char * (length - len(value)) + value


def left_aligning(value: str, length: int, char: str = " "):
    value = str(value)
    length = max(length, len(value))
    return value + char * (length - len(value))


def confirm(text: str):
    text += "\nPlease type `Yes` to confirm this action: "
    return input(text).lower() == "yes"
