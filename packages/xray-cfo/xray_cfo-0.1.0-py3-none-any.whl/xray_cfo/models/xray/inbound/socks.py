from pydantic import Field

from .._base import XBase


class SocksAccount(XBase):
    user: str
    password: str = Field(serialization_alias="pass")


class XSocksIn(XBase):
    auth: str
    accounts: list[SocksAccount]
    udp: bool = False
    ip: str
    user_level: int = Field(0, serialization_alias="userLevel")
