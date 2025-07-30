from contextvars import ContextVar
from os import environ
from typing import TYPE_CHECKING, Final, TypeAlias, TypeVar

if TYPE_CHECKING:
    StrDict: TypeAlias = dict[str, str]

_T = TypeVar("_T")

_progname: Final[ContextVar[str]] = ContextVar("progname")
_request_id: Final[ContextVar[str]] = ContextVar("request_id")
_sentinel: Final[str] = "\x00"


def _parse_log_env_extra() -> "StrDict":
    if not (log_env_extra := environ.get("LOG_ENV_EXTRA")):
        return {}

    result: Final[StrDict] = {}
    for extra in log_env_extra.split(","):
        field, environ_key = extra.split(":", 1)
        if not (value := environ.get(environ_key.strip())):
            continue

        result[field.strip()] = value
    return result


def get_env_extra() -> "StrDict":
    result: StrDict = {
        _progname.name: get_progname(default=_sentinel),
        _request_id.name: get_request_id(default=_sentinel),
    }
    result |= _parse_log_env_extra()
    return result


def get_extra_from_environ() -> "StrDict":
    return {key: value for key, value in get_env_extra().items() if value != _sentinel}


def set_extra_to_environ(key: str, value: str) -> None:
    if key == _progname.name:
        set_progname(value=value)
    elif key == _request_id.name:
        set_request_id(value=value)
    else:
        environ[key] = value


# -------------------


def get_progname(*, default: _T) -> str | _T:
    return _progname.get(default)


def get_request_id(*, default: _T) -> str | _T:
    return _request_id.get(default)


def set_progname(*, value: str) -> None:
    _progname.set(value)


def set_request_id(*, value: str) -> None:
    _request_id.set(value)
