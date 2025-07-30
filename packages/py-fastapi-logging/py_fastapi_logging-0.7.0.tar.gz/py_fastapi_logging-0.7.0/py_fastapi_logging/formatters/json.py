import json
from types import TracebackType
from typing import TYPE_CHECKING, Any

from py_fastapi_logging.formatters.base import BaseFormatter
from py_fastapi_logging.utils.extra import get_env_extra

if TYPE_CHECKING:
    from logging import LogRecord
    from typing import TypeAlias, TypedDict, Union  # noqa: I251

    class _ExcInfoPayload(TypedDict):
        exception: dict[str, Any]

    class _LogRecord(LogRecord):
        """
        Подкласс :py:class:`logging.LogRecord` с дополнительными типизированными параметрами.
        """

        tags: list[str]
        payload: dict[str, Any]

    _SysExcInfoType: TypeAlias = Union[
        tuple[type[BaseException], BaseException, TracebackType | None],
        tuple[None, None, None],
    ]


class JSONLogFormatter(BaseFormatter):
    def _format_exc_info_payload(self, exc_info: "_SysExcInfoType", /) -> "_ExcInfoPayload":
        exc_type, exc_value, _ = exc_info
        try:
            return {
                "exception": {
                    "class": exc_type.__name__,  # type: ignore[union-attr]
                    "message": str(exc_value),
                    "backtrace": self.formatException(exc_info),
                }
            }
        except Exception:
            return {
                "exception": {
                    "class": None,
                    "message": repr(exc_info),
                    "backtrace": None,
                }
            }

    def _format_log(self, record: "_LogRecord") -> str:  # type: ignore[override]
        json_log_fields: dict[str, Any] = {
            "timestamp": self._format_date(record.created),
            "level": record.levelname,
        }

        for key in get_env_extra().keys():
            if hasattr(record, key):
                json_log_fields[key] = getattr(record, key)
            elif key == "progname":
                json_log_fields[key] = record.module

        json_log_fields["tags"] = record.tags if hasattr(record, "tags") else []

        if hasattr(record, "payload"):
            json_log_fields["payload"] = record.payload
        elif exc_info := record.exc_info:
            json_log_fields["payload"] = self._format_exc_info_payload(exc_info)
        elif hasattr(record, "message"):
            json_log_fields["payload"] = {"message": record.message}
        elif hasattr(record, "msg"):
            json_log_fields["payload"] = {"message": record.getMessage()}

        return json.dumps(json_log_fields, ensure_ascii=False, separators=(",", ":"), default=str)
