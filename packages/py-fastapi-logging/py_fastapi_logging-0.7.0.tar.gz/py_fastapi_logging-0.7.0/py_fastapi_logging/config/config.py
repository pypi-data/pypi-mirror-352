from collections.abc import Iterable
from functools import cached_property
from logging import FileHandler, Handler, Logger, StreamHandler, basicConfig, getLogger
from logging import root as root_logger
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from os import PathLike, environ
from pathlib import Path
from typing import Any, ClassVar, Literal, TypeAlias, cast

from py_fastapi_logging.formatters.json import JSONLogFormatter
from py_fastapi_logging.formatters.simple import SimpleLogFormatter
from py_fastapi_logging.utils.extra import set_progname

LoggingLevel: TypeAlias = Literal["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG", "NOTSET"]
HandlerName: TypeAlias = Literal["simple", "json-stdout", "json", "stderr"]


class LogConfigure:
    DEFAULT_OUTPUTS: ClassVar[str] = "json,stderr"
    FORMAT_MAP: ClassVar[dict[str, HandlerName]] = {"console": "stderr"}

    def __init__(
        self,
        app_name: str,
        *,
        filename: str | PathLike[str] | None = None,
        level: LoggingLevel | None = None,
        rotate_mb: int | None = None,
        rotate_when: str | None = None,
        backup_count: int = 5,
        log_output: str | None = None,
        exclude_fields: Iterable[str] | None = None,
        apply_format_extension_to_filename: bool = False,
    ) -> None:
        self._app_name: str = app_name
        self._filename: Path | None = Path(filename) if filename else None
        self._level: LoggingLevel | None = level
        self._rotate_mb: int | None = rotate_mb
        self._rotate_when: str | None = rotate_when
        self._backup_count: int = backup_count
        self._log_output: str | None = log_output
        self._exclude_fields: list[str] | None = list(exclude_fields) if exclude_fields is not None else None
        self._apply_format_extension_to_filename = apply_format_extension_to_filename

    @property
    def app_name(self) -> str:
        return self._app_name

    @property
    def level(self) -> LoggingLevel:
        return cast(LoggingLevel, environ.get("LOG_LEVEL", self._level or "INFO").upper())

    @property
    def base_app_name(self) -> str:
        app_name, *_ = self._app_name.split(".", 1)
        return app_name

    @property
    def rotate_mb(self) -> int | None:
        file_size = environ.get("LOG_FILE_SIZE")
        if file_size:
            return int(file_size)
        return self._rotate_mb

    @property
    def backup_count(self) -> int:
        files_count = environ.get("LOG_FILES_COUNT")
        if files_count:
            return int(files_count)
        return self._backup_count

    @cached_property
    def directory(self) -> Path:
        if log_dir := environ.get("LOG_DIR"):
            return Path(log_dir)

        if self._filename and self._filename.is_absolute():
            return self._filename.parent

        return Path("/var/log/", self.base_app_name)

    def get_filename(self, suffix: str) -> Path:
        if not (filename := self._filename):
            filename = Path(environ.get("LOG_FILENAME", f"{self.base_app_name}.log"))

        file_path = self.directory / filename
        if self._apply_format_extension_to_filename:
            file_path = file_path.with_suffix(suffix)
        return file_path

    def _get_file_handler(self, suffix: str, *, encoding: str = "utf-8") -> Handler:
        filename: Path = self.get_filename(suffix)

        if self.backup_count > 0:
            if self.rotate_mb and self.rotate_mb > 0:
                return RotatingFileHandler(
                    filename,
                    maxBytes=self.rotate_mb * 1024 * 1024,
                    backupCount=self.backup_count,
                    encoding=encoding,
                )
            elif self._rotate_when:
                return TimedRotatingFileHandler(
                    filename,
                    when=self._rotate_when,
                    backupCount=self.backup_count,
                    encoding=encoding,
                )

        return FileHandler(filename, encoding=encoding)

    def get_handler(self, name: HandlerName) -> Handler:
        handler: Handler

        match name:
            case "simple":
                handler = self._get_file_handler(".txt")
                handler.setFormatter(SimpleLogFormatter())
            case "json-stdout":
                handler = StreamHandler()
                handler.setFormatter(JSONLogFormatter())
            case "json":
                handler = self._get_file_handler(".json")
                handler.setFormatter(JSONLogFormatter())
            case "stderr":
                handler = StreamHandler()
                handler.setFormatter(SimpleLogFormatter())
            case _:
                raise ValueError(f"Unknown handler type {name!r}")

        return handler

    def normalize_format_names(self, names: str) -> list[HandlerName]:
        return [self.FORMAT_MAP.get(name, cast(HandlerName, name)) for name in names.lower().split(",")]

    @property
    def formats(self) -> list[HandlerName]:
        if not (names := self._log_output):
            names = environ.get("LOG_OUTPUT") or environ.get("LOG_FORMAT") or self.DEFAULT_OUTPUTS

        list_formats: list[HandlerName] = []
        for fmt in self.normalize_format_names(names):
            if fmt is None:
                raise ValueError(f"Unknown handler type {fmt!r}")

            list_formats.append(fmt)
        return list_formats

    def get_handlers(self, names: Iterable[HandlerName]) -> list[Handler]:
        return [self.get_handler(name) for name in names]

    @property
    def default_logger_level(self) -> str | None:
        if level := (environ.get("LOGGING_DEFAULT_LEVEL") or environ.get("LOG_DEFAULT_LEVEL")):
            level = level.upper()
        return level

    @property
    def default_logger_output(self) -> str | None:
        return environ.get("LOGGING_DEFAULT_HANDLER") or environ.get("LOG_DEFAULT_OUTPUT")


def init_logger(app_name: str, **kwargs: Any) -> LogConfigure:
    config: LogConfigure = LogConfigure(app_name=app_name, **kwargs)

    for name in root_logger.manager.loggerDict:
        logger: Logger = getLogger(name)
        for handler in logger.handlers.copy():
            logger.removeHandler(handler)
            handler.close()

    config.directory.mkdir(parents=True, exist_ok=True)
    basicConfig(handlers=config.get_handlers(config.formats), level=config.level, force=True)
    set_progname(value=config.app_name)
    return config
