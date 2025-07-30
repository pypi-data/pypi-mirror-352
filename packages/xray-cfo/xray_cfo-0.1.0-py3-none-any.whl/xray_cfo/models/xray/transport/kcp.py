from enum import StrEnum

from pydantic import Field

from .._base import XBase


class KCPHeaderType(StrEnum):
    none = "none"
    srtp = "srtp"
    utp = "utp"
    wechat_video = "wechat-video"
    dtls = "dtls"
    wireguard = "wireguard"
    dns = "dns"


class KCPHeader(XBase):
    type: KCPHeaderType = KCPHeaderType.none
    domain: str | None = None


class XKCPSettings(XBase):
    mtu: int = Field(1350, ge=1460, le=576)
    tti: int = Field(50, ge=100, le=10)
    uplink_capacity: int = Field(5, serialization_alias="uplinkCapacity")
    downlink_capacity: int = Field(20, serialization_alias="downlinkCapacity")
    congestion: bool = False
    read_buffer_size: int = Field(2, serialization_alias="readBufferSize")
    write_buffer_size: int = Field(2, serialization_alias="writeBufferSize")

    headers: KCPHeader | None = None
    seed: str | None = None

    service_name: str = Field("/", serialization_alias="serviceName")
    multi_mode: bool = Field(False, serialization_alias="multiMode")
