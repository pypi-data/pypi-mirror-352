import ipaddress
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from ._base import XBase


class QueryStrategy(StrEnum):
    use_ip = "UseIP"
    use_ip_v4 = "UseIPv4"
    use_ip_v6 = "UseIPv6"


class DnsServerObject(XBase):
    tag: str
    address: str
    port: int | None = None
    domains: list[str] | None = None
    expect_ips: list[str] | None = Field(None, serialization_alias="expectIPs")
    skip_fallback: bool = Field(False, serialization_alias="skipFallback")
    client_ip: str | None = Field(None, serialization_alias="clientIp")
    query_strategy: QueryStrategy | None = Field(None, serialization_alias="queryStrategy")
    timeout_ms: int = Field(4000, serialization_alias="timeoutMs")
    allow_unexpected_ips: bool = Field(False, serialization_alias="allowUnexpectedIPs")

    @field_validator("address")
    def validate_address(cls, v: str) -> str:
        if not v:
            raise ValueError("address cannot be empty")

        if v.startswith(("tcp://", "tcp+local://", "https://", "https+local://",
                         "h2c://", "quic+local://")):
            return v

        if v in ("fakedns", "localhost"):
            return v

        # Assume IP or domain name
        try:
            host, port_part = v.rsplit(":", 1)
            ipaddress.ip_address(host)
            return v
        except ValueError:
            # Not an IP, assume it's a domain
            return v

    @field_validator("domains")
    def validate_domains(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v

        for domain in v:
            if not domain.startswith(("domain:", "regexp:", "keyword:", "geosite:")):
                raise ValueError(
                    f"Invalid domain format: {domain}. Must start with domain:, regexp:, keyword:, or geosite:")
        return v

    @field_validator("expect_ips")
    def validate_expect_ips(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v

        for ip in v:
            if not ip.startswith(("geoip:", "cidr:")) and not cls._is_valid_ip_or_cidr(ip):
                raise ValueError(f"Invalid expectIPs entry: {ip}. Must be geoip:*, cidr:*, or a valid IP/CIDR")
        return v

    @field_validator("client_ip")
    def validate_client_ip(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            ip = ipaddress.ip_address(v)
            if ip.is_private:
                raise ValueError("clientIp must be a public IP address")
        except ValueError as e:
            raise ValueError(f"Invalid clientIp: {e}")
        return v

    @staticmethod
    def _is_valid_ip_or_cidr(value: str) -> bool:
        try:
            if "/" in value:
                ipaddress.ip_network(value, strict=False)
            else:
                ipaddress.ip_address(value)
            return True
        except ValueError:
            return False


class XDns(XBase):
    hosts: dict[str, list[str] | str] | None = None
    servers: list[str | DnsServerObject] | None = None
    client_ip: str | None = Field(None, serialization_alias="clientIp")
    query_strategy: QueryStrategy | None = Field(None, serialization_alias="queryStrategy")
    disable_cache: bool = Field(False, serialization_alias="disableCache")
    disable_fallback: bool = Field(False, serialization_alias="disableFallback")
    disable_fallback_if_match: bool = Field(False, serialization_alias="disableFallbackIfMatch")
    tag: str

    @field_validator("client_ip")
    def validate_client_ip_global(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            ip = ipaddress.ip_address(v)
            if ip.is_private:
                raise ValueError("clientIp must be a public IP address")
        except ValueError as e:
            raise ValueError(f"Invalid clientIp: {e}")
        return v

    @model_validator(mode="after")
    def validate_query_strategy_conflicts(self) -> "XDns":
        servers = self.servers
        strategy = self.query_strategy

        if not servers or strategy is None:
            return self

        for server in servers:
            if isinstance(server, DnsServerObject) and server.expect_ips:
                server_strategy = server.query_strategy
                if (
                        (strategy == QueryStrategy.use_ip_v4 and server_strategy == QueryStrategy.use_ip_v6) or
                        (strategy == QueryStrategy.use_ip_v6 and server_strategy == QueryStrategy.use_ip_v4)
                ):
                    raise ValueError(
                        f"Conflict between global queryStrategy '{strategy}' and server-specific '{server_strategy}'"
                    )
        return self
