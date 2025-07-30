from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from xray_cfo.models.xray.enums import Network

from ._base import XBase


class DomainStrategy(StrEnum):
    AsIs = "AsIs"
    IPIfNonMatch = "IPIfNonMatch"
    IPOnDemand = "IPOnDemand"


class DomainMatcher(StrEnum):
    hybrid = "hybrid"
    linear = "linear"


class Protocol(StrEnum):
    http = "http"
    tls = "tls"
    quic = "quic"
    bittorrent = "bittorrent"


class Rule(XBase):
    domain_matcher: DomainMatcher = Field(
        DomainMatcher.hybrid, serialization_alias="domainMatcher"
    )
    type: str = "field"
    domain: list[str] | None = None
    ip: list[str] | None = None
    port: str | int = None
    sourcePort: str | int = None
    network: Network | None = None
    source: list[str] | None = None
    user: list[str] | None = None
    inboundTag: list[str] | None = None
    protocol: list[Protocol] | None = None
    attrs: dict[str, str] | None = None
    outboundTag: str | None = None
    balancerTag: str | None = None
    ruleTag: str | None = None


class StrategyType(StrEnum):
    random = "random"
    roundRobin = "roundRobin"
    leastPing = "leastPing"
    leastLoad = "leastLoad"


class Cost(XBase):
    regexp: bool
    match: str
    value: Decimal


class StrategySettings(XBase):
    expected: int
    maxRTT: str
    tolerance: Decimal
    baselines: list[str]
    costs: list[Cost]


class Strategy(XBase):
    type: StrategyType
    settings: StrategySettings


class Balancer(XBase):
    tag: str
    selector: list[str] | None = None
    fallbackTag: str
    strategy: list[Strategy]


class XRouting(XBase):
    domain_strategy: DomainStrategy = Field(
        DomainStrategy.AsIs, serialization_alias="domainStrategy"
    )
    domain_matcher: DomainMatcher = Field(
        DomainMatcher.hybrid, serialization_alias="domainMatcher"
    )
    rules: list[Rule] | None = None
    balancers: list[Balancer] | None = None
