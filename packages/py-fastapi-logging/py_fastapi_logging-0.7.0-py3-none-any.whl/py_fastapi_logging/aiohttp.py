import logging
from collections.abc import Iterable, Mapping
from functools import lru_cache
from time import time
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Final, NamedTuple, TypeAlias

from multidict import MultiDictProxy
from yarl import URL

from py_fastapi_logging.data_filter import DataFilter

try:
    from aiohttp import TraceConfig, hdrs
except ImportError as exc:
    raise ImportError("Using this module requires the aiohttp library.") from exc

if TYPE_CHECKING:
    from aiohttp import ClientSession, TraceRequestChunkSentParams, TraceRequestEndParams, TraceRequestStartParams

    _ParamsDict: TypeAlias = dict[str, str | list[str]]

HTTP_METHODS_WITH_BODY: Final = (hdrs.METH_PATCH, hdrs.METH_POST, hdrs.METH_PUT)


class _Request(NamedTuple):
    service_name: str | None
    request_id: str | None
    method: str
    url: URL
    headers: Mapping
    start_time: float


def create_logging_trace_config(
    service_name: str | None,
    filtered_fields: Iterable[str] = frozenset(),
    marker_filtered: str = "[filtered]",
) -> TraceConfig:
    def context_factory(**kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(
            service_name=service_name,
            data_filter=DataFilter(filtered_fields=filtered_fields, marker_filtered=marker_filtered),
            **kwargs,
        )

    trace_config: TraceConfig = TraceConfig(context_factory)  # type: ignore[arg-type]
    trace_config.on_request_start.append(_on_request_start)
    trace_config.on_request_chunk_sent.append(_on_request_chunk_sent)
    trace_config.on_request_end.append(_on_request_end)
    return trace_config


def _convert_params_to_dict(params_mulitdict: MultiDictProxy) -> "_ParamsDict":
    params_dict: "_ParamsDict" = {}
    for key in params_mulitdict.keys():
        values = params_mulitdict.getall(key)
        params_dict[key] = values[0] if len(values) == 1 else values
    return params_dict


def _make_tags_list(*tags: str | None) -> list[str]:
    return list(filter(None, tags))


async def _on_request_start(
    session: "ClientSession",
    context: SimpleNamespace,
    params: "TraceRequestStartParams",
) -> None:
    context.request = _Request(
        service_name=context.service_name,
        request_id=params.headers.get("X-Request-Id"),
        method=params.method,
        url=params.url,
        headers=params.headers,
        start_time=time(),
    )

    content_length = params.headers.get("Content-Length")
    if content_length or params.method in HTTP_METHODS_WITH_BODY:
        return

    request: _Request = context.request
    data_filter: DataFilter = context.data_filter
    filtered_url = _filter_url(data_filter, str(request.url))
    query_params = _convert_params_to_dict(request.url.query)

    logging.info(
        f"Request {request.method} {filtered_url}",
        extra={
            "tags": _make_tags_list("SERVICE", request.service_name, "REQUEST"),
            "request_id": request.request_id,
            "payload": {
                "method": request.method,
                "url": str(request.url.with_query(None)),
                "params": _filter_dict(data_filter, query_params),
            },
        },
    )


async def _on_request_chunk_sent(
    session: "ClientSession",
    context: SimpleNamespace,
    params: "TraceRequestChunkSentParams",
) -> None:
    request: _Request = context.request
    data_filter: DataFilter = context.data_filter

    content_length = request.headers.get("Content-Length")
    if not (content_length or params.method in HTTP_METHODS_WITH_BODY):
        return

    try:
        request_body = params.chunk.decode("utf-8")
    except Exception:
        logging.exception("Failed to decode request body")
        request_body = "(failed to decode)"

    filtered_url = _filter_url(data_filter, str(request.url))
    query_params = _convert_params_to_dict(request.url.query)

    logging.info(
        f"Request {request.method} {filtered_url}",
        extra={
            "tags": _make_tags_list("SERVICE", request.service_name, "REQUEST"),
            "request_id": request.request_id,
            "payload": {
                "method": request.method,
                "url": str(request.url.with_query(None)),
                "params": _filter_dict(data_filter, query_params),
                "body": _filter_request_body(data_filter, request_body, request.headers),
            },
        },
    )


async def _on_request_end(
    session: "ClientSession",
    context: SimpleNamespace,
    params: "TraceRequestEndParams",
) -> None:
    request: _Request = context.request
    data_filter: DataFilter = context.data_filter
    request_time_ms: int = round((time() - request.start_time) * 1000)
    response_body = await params.response.text()
    filtered_url = _filter_url(data_filter, str(request.url))

    logging.info(
        f"Response {request.method} {filtered_url}",
        extra={
            "tags": _make_tags_list("SERVICE", request.service_name, "RESPONSE"),
            "request_id": request.request_id,
            "payload": {
                "status": params.response.status,
                "response_time": f"{request_time_ms}ms",
                "response_body": _filter_response_body(data_filter, response_body),
            },
        },
    )


def _filter_request_body(data_filter: DataFilter, body: str, headers: Mapping) -> str:
    try:
        return data_filter.filter_request_body(body, headers)
    except Exception:
        logging.exception("Failed to filter private data in request body")
        return "(failed to filter private data)"


def _filter_response_body(data_filter: DataFilter, body: str) -> str:
    try:
        return data_filter.filter_json_body(body)
    except Exception:
        logging.exception("Failed to filter private data in response body")
        return "(failed to filter private data)"


def _filter_dict(data_filter: DataFilter, data: dict) -> dict:
    try:
        return data_filter.filter_data(data)
    except Exception:
        logging.exception("Failed to filter private data")
        return {}


@lru_cache
def _filter_url(data_filter: DataFilter, url: str) -> str:
    return data_filter.filter_url_encoded_string(url)
