from pydantic import Field

from .._base import XBase


class HttpAccount(XBase):
    user: str
    password: str = Field(serialization_alias="pass")


class XHttpIn(XBase):
    accounts: list[HttpAccount]
    allow_transparent: bool = Field(False, serialization_alias="allowTransparent:")
    user_level: int = Field(0, serialization_alias="userLevel")
