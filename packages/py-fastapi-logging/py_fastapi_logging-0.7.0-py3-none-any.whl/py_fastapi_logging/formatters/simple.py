from typing import TYPE_CHECKING, Any

from py_fastapi_logging.formatters.base import BaseFormatter

if TYPE_CHECKING:
    from logging import LogRecord

    class _LogRecord(LogRecord):
        """
        Подкласс :py:class:`logging.LogRecord` с дополнительными типизированными параметрами.
        """

        progname: str
        request_id: str
        tags: list[str]
        payload: dict[str, Any]


class SimpleLogFormatter(BaseFormatter):
    def _format_log(self, record: "_LogRecord") -> str:  # type: ignore[override]
        output: str = f"[{self._format_date(record.created)}] {record.levelname} "
        output += f" -- {record.progname if hasattr(record, 'progname') else record.module}: "

        if hasattr(record, "request_id"):
            output += f"[{record.request_id!s}] "

        if hasattr(record, "tags"):
            output += f"{record.tags!r} "

        record.message = record.getMessage()
        output += self.formatMessage(record)

        if exc_info := record.exc_info:
            _, exception, _ = exc_info
            output += "\n".join((str(exception), self.formatException(exc_info)))
            del exception, exc_info

        if hasattr(record, "payload"):
            output += f"{record.payload!r}"

        return output
