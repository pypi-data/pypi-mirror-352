from enum import StrEnum

from pydantic import Field

from xray_cfo.models.xray.transport import XStreamSettings

from .._base import XBase
from .dokodemo import XDokoDemoIn
from .http import XHttpIn
from .shadowsocks import XShadowsocksIn
from .socks import XSocksIn
from .trojan import XTrojanIn
from .vless import XVlessIn
from .vmess import XVmessIn
from .wireguard import WireGuardIn


class InProtocols(StrEnum):
    dokodemo = "dokodemo-door"
    http = "http"
    shadowsocks = "shadowsocks"
    mixed = "mixed"
    vless = "vless"
    vmess = "vmess"
    trojan = "trojan"
    wireguard = "wireguard"


class SniffingDest(StrEnum):
    http = "http"
    tls = "tls"
    quic = "quic"
    fakedns = "fakedns"
    others = "fakedns+others"


def get_default_sniffing_dest():
    return [SniffingDest.http, SniffingDest.tls]


class SniffingObject(XBase):
    enabled: bool = True
    dest_override: list[SniffingDest] | None = Field(
        default_factory=get_default_sniffing_dest, serialization_alias="destOverride"
    )
    metadata_only: bool = Field(False, serialization_alias="metadataOnly")
    domains_excluded: list[str] | None = Field(
        None, serialization_alias="domainsExcluded"
    )
    route_only: bool = Field(False, serialization_alias="routeOnly")


class AllocateStrategy(StrEnum):
    always = "always"
    random = "random"


class AllocateObject(XBase):
    strategy: AllocateStrategy = AllocateStrategy.always
    refresh: int = 5
    concurrency: int = 3


class XInboundObject(XBase):
    listen: str
    port: int | str
    protocol: InProtocols
    settings: (
        XDokoDemoIn
        | XHttpIn
        | XShadowsocksIn
        | XSocksIn
        | XTrojanIn
        | XVlessIn
        | XVmessIn
        | WireGuardIn
    )
    stream_settings: XStreamSettings | None = Field(
        None, serialization_alias="streamSettings"
    )
    tag: str
    sniffing: SniffingObject | None = None
    allocate: AllocateObject | None = None
