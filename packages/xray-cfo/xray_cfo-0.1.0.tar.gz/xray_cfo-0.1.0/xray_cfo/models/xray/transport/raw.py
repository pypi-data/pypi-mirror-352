from pydantic import Field

from .._base import XBase


class RawNoneHeader(XBase):
    type: str = "none"


def base_path_list():
    return ["/"]


class RawHttpRequest(XBase):
    version: str = "1.1"
    method: str = "GET"
    path: list[str] = Field(default_factory=base_path_list)
    headers: dict[str, list[str] | str]


class RawHttpResponse(XBase):
    version: str = "1.1"
    status: str = "200"
    reason: str = "OK"
    headers: dict[str, list[str] | str]


class RawHttpHeader(XBase):
    type: str = "http"
    request: RawHttpRequest | None = None
    response: RawHttpResponse | None = None


class XRawSettings(XBase):
    accept_proxy_protocol: bool = Field(False, serialization_alias="acceptProxyProtocol")
    headers: RawNoneHeader | None = None
