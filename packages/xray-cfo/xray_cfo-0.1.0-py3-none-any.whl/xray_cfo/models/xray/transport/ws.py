from pydantic import Field

from .._base import XBase


class XWebSocketSettings(XBase):
    accept_proxy_protocol: bool = Field(False, serialization_alias="acceptProxyProtocol")
    path: str = "/"
    host: str | None = None
    headers: dict[str, str] | None = None
    heartbeat_period: int = Field(0, serialization_alias="heartbeatPeriod")
