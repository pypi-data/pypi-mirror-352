from enum import StrEnum

from pydantic import Field

from .._base import XBase


class SockoptTProxy(StrEnum):
    redirect = "redirect"
    tproxy = "tproxy"
    off = "off"


class SockoptDomainStrategy(StrEnum):
    AsIs = "AsIs"
    UseIP = "UseIP"
    UseIPv6v4 = "UseIPv6v4"
    UseIPv6 = "UseIPv6"
    UseIPv4v6 = "UseIPv4v6"
    UseIPv4 = "UseIPv4"
    ForceIP = "ForceIP"
    ForceIPv6v4 = "ForceIPv6v4"
    ForceIPv6 = "ForceIPv6"
    ForceIPv4v6 = "ForceIPv4v6"
    ForceIPv4 = "ForceIPv4"


class CustomSockopt(XBase):
    system: str
    type: str
    level: str
    opt: str
    value: str


class Sockopt(XBase):
    mark: int
    tcp_max_seg: int = Field(1440, serialization_alias="tcpMaxSeg")
    tcp_fast_open: bool | int = Field(False, serialization_alias="tcpFastOpen")
    tproxy: SockoptTProxy = SockoptTProxy.off
    domain_strategy: SockoptDomainStrategy = Field(SockoptDomainStrategy.AsIs, serialization_alias="domainStrategy")
    dialer_proxy: str = Field("", serialization_alias="dialerProxy")
    accept_proxy_protocol: bool = Field(False, serialization_alias="acceptProxyProtocol")
    tcp_keep_alive_interval: int = Field(0, serialization_alias="tcpKeepAliveInterval")
    tcp_keep_alive_idle: int = Field(300, serialization_alias="tcpKeepAliveIdle")
    tcp_user_timeout: int = Field(10000, serialization_alias="tcpUserTimeout")
    tcpcongestion: str = "bbr"
    interface: int = ""
    v6Only: bool = Field(False, serialization_alias="V6Only")
    tcp_window_clamp: int | None = Field(None, serialization_alias="tcpWindowClamp")
    tcp_mptcp: bool = Field(False, serialization_alias="tcpMptcp")
    tcp_no_delay: bool = Field(False, serialization_alias="tcpNoDelay")
    custom_sockopt: list[CustomSockopt] | None = Field(None, serialization_alias="customSockopt")
