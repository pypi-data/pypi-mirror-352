from typing import TypedDict


class BaseJsonLogSchema(TypedDict):
    timestamp: str
    level: str
    progname: str | None
    request_id: str | None
    tags: list[str]
