from pydantic import Field

from .._base import XBase


class Peer(XBase):
    allowed_ips: list[str] = Field(serialization_alias="allowedIPs")
    keep_alive: int
    pre_shared_key: str = Field(serialization_alias="preSharedKey")
    private_key: str = Field(serialization_alias="publicKey")
    public_key: str = Field(serialization_alias="publicKey")


class WireGuardIn(XBase):
    secret_key: str = Field(serialization_alias="secretKey")
    peers: list[Peer]
    mtu: int = 1420
