from enum import StrEnum

from pydantic import Field

from .._base import XBase


class DomainStrategy(StrEnum):
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


class Noise(XBase):
    type: str
    packet: str
    delay: str


class XFreedomOut(XBase):
    domain_strategy: DomainStrategy = Field(
        DomainStrategy.AsIs, serialization_alias="domainStrategy"
    )
    redirect: str = ""
    user_level: int = Field(0, serialization_alias="userLevel")
    fragment: dict | None = None
    noises: list[Noise] = Field(default_factory=list)

    proxy_protocol: int = Field(0, serialization_alias="proxyProtocol")
