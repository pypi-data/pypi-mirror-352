from typing import Final
from uuid import uuid4

DEFAULT_DELIMITER: Final[str] = "#"


def generate_request_id(
    *,
    prefix: str | None = None,
    suffix: str | None = None,
    delimiter: str = DEFAULT_DELIMITER,
) -> str:
    return "".join(
        (
            f"{prefix}{delimiter}" if prefix else "",
            str(uuid4()),
            f"{delimiter}{suffix}" if suffix else "",
        )
    )
