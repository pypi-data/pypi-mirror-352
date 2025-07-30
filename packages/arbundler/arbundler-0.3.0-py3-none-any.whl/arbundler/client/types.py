from msgspec import Struct


class ApiObject(Struct, kw_only=True, rename="camel"):
    """
    Base class for the API that uses camelCase, declaring each mixin separately to follow Single Inheritance
    https://learn.microsoft.com/en-us/cpp/cpp/single-inheritance?view=msvc-170
    """

    ...


class UploadResponse(ApiObject):
    id: str
    owner: str
    winc: int
    timestamp: int

    data_caches: list[str]
    fast_finality_indexes: list[str]

    deadline_height: int
    version: str

    signature: str
    public: str
