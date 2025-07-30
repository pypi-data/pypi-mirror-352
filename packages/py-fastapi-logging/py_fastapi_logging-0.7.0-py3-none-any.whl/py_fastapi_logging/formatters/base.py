from abc import ABCMeta, abstractmethod
from datetime import datetime, timezone
from logging import Formatter, LogRecord

from py_fastapi_logging.utils.extra import get_extra_from_environ


class BaseFormatter(Formatter, metaclass=ABCMeta):
    __slots__: tuple[str, ...] = ()

    @abstractmethod
    def _format_log(self, record: LogRecord) -> str:
        raise NotImplementedError

    def _update_extra(self, record: LogRecord) -> LogRecord:
        for extra_key, extra_value in get_extra_from_environ().items():
            if not hasattr(record, extra_key):
                setattr(record, extra_key, extra_value)
        return record

    def _format_date(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).astimezone(tz=timezone.utc).replace(tzinfo=None).isoformat() + "Z"

    def format(self, record: LogRecord) -> str:
        return self._format_log(self._update_extra(record))
