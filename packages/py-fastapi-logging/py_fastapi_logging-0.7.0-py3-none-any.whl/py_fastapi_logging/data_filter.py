import json
import re
from collections.abc import Iterable, Mapping, MutableMapping, MutableSequence
from typing import Any

from py_fastapi_logging.utils.parse_header import parse_header


class DataFilter:
    _filtered_fields: Iterable
    _marker_filtered: str
    _multipart_body_part_pattern: re.Pattern
    _url_encoded_body_pattern: re.Pattern

    def __init__(self, filtered_fields: Iterable, marker_filtered: str) -> None:
        self._filtered_fields = filtered_fields
        self._marker_filtered = marker_filtered

        fields_regex = "|".join(self._filtered_fields)
        self._multipart_body_part_pattern = re.compile(
            rf"(^[\r\n]*Content-Disposition: *form-data; *name=\"(?:{fields_regex})\".*?[\r\n]+).*?(\r\n|\r|\n)$",
            flags=re.DOTALL + re.IGNORECASE,
        )
        self._url_encoded_body_pattern = re.compile(rf"\b({fields_regex})=[^&]*")

    def filter_request_body(self, body: str, headers: Mapping) -> str:
        if not self._filtered_fields:
            return body

        if content_type := headers.get("content-type"):
            media_type, content_options = parse_header(content_type)  # type: ignore[no-untyped-call]
            if media_type == "multipart/form-data" and (boundary := content_options.get("boundary")):
                return self._filter_multipart_body(body, boundary)

        if self._is_json_body(body):
            return self.filter_json_body(body)

        return self.filter_url_encoded_string(body)

    def filter_json_body(self, body: str) -> str:
        if not self._filtered_fields or not self._is_json_body(body):
            return body

        request_json: Any = json.loads(body)
        response_json: Any = self.filter_data(request_json)
        return json.dumps(response_json, ensure_ascii=False, separators=(",", ":"))

    def filter_data(self, data: Any) -> Any:
        if not self._filtered_fields:
            return data

        if isinstance(data, MutableMapping):
            return {
                key: self.filter_data(value) if key not in self._filtered_fields else self._marker_filtered
                for key, value in data.items()
            }
        elif isinstance(data, MutableSequence):
            return list(map(self.filter_data, data))
        else:
            return data

    def filter_url_encoded_string(self, string: str) -> str:
        if not self._filtered_fields:
            return string

        return self._url_encoded_body_pattern.sub(rf"\1={self._marker_filtered}", string)

    def _is_json_body(self, body: str) -> bool:
        return body.startswith(("[", "{"))

    def _filter_multipart_body(self, body: str, boundary: str) -> str:
        separator = f"--{boundary}"
        filtered_parts = map(
            self._filter_multipart_body_part,
            body.split(separator),
        )
        return separator.join(filtered_parts)

    def _filter_multipart_body_part(self, part: str) -> str:
        return self._multipart_body_part_pattern.sub(rf"\1{self._marker_filtered}\2", part)
