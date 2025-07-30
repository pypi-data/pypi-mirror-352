import ipaddress

from pydantic import Field, field_validator, model_validator

from ._base import XBase


class XFakeDns(XBase):
    ip_pool: str = Field(serialization_alias="ipPool")
    pool_size: int = Field(65535, serialization_alias="poolSize")

    @field_validator("ip_pool")
    def validate_ip_pool(cls, v: str) -> str:
        try:
            ipaddress.ip_network(v, strict=False)
        except ValueError:
            raise ValueError(f"Invalid CIDR for ipPool: {v}")
        return v

    @model_validator(mode="after")
    def validate_pool_size(self) -> "XFakeDns":
        if self.pool_size <= 0:
            raise ValueError("poolSize must be a positive integer"
                             )
        if self.ip_pool:
            network = ipaddress.ip_network(self.ip_pool, strict=False)
            total_ips = network.num_addresses
            if self.pool_size > total_ips:
                raise ValueError(f"poolSize ({self.pool_size}) cannot exceed number of addresses in ipPool ({total_ips})")
        return self
