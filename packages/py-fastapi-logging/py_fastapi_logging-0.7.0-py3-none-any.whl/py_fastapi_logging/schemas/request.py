from typing import Any, TypedDict


class RequestPayload(TypedDict):
    method: str
    path: str
    host: str
    params: dict[str, Any] | None
    body: str
