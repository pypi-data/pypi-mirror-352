from enum import StrEnum

from pydantic import Field

from xray_cfo.models.xray.transport import XStreamSettings

from .._base import XBase
from .blackhole import BlackHoleOut
from .freedom import XFreedomOut


class XUDPProxyUDP443(StrEnum):
    reject = "reject"
    allow = "allow"
    skip = "skip"


class MuxObject(XBase):
    enabled: bool = True
    concurrency: int = 8
    xudp_concurrency: int = Field(16, serialization_alias="xudpConcurrency")
    xudp_proxy_udp_443: XUDPProxyUDP443 = Field(
        XUDPProxyUDP443.reject, serialization_alias="xudpProxyUDP443"
    )


class XOutboundObject(XBase):
    send_through: str = Field("0.0.0.0", serialization_alias="sendThrough")
    protocol: str
    tag: str
    settings: BlackHoleOut | XFreedomOut
    stream_settings: XStreamSettings | None = Field(
        None, serialization_alias="streamSettings"
    )
    proxy_settings: dict | None = Field(None, serialization_alias="proxySettings")
    mux: MuxObject | None = None
