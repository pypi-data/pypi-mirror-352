from typing import Any, TypeVar

import msgspec

T = TypeVar("T")


def encode_decode_json(obj: Any) -> Any:
    return msgspec.json.decode(msgspec.json.encode(obj))


def encode_json(obj: Any) -> bytes:
    return msgspec.json.encode(obj)


def decode_json_loosely(data: str | bytes, t: type[T]) -> T:
    return msgspec.json.decode(data, strict=False, type=t)


def convert_obj_loosely(data: Any, t: type[T]) -> T:
    return msgspec.convert(data, t, strict=False)
