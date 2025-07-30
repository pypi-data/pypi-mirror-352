from pydantic import Field

from xray_cfo.models.xray.enums import Network

from .._base import XBase


class XDokoDemoIn(XBase):
    address: str
    port: int | str
    network: Network
    follow_redirect: bool = Field(serialization_alias="followRedirect")
    user_level: int = Field(serialization_alias="userLevel")
