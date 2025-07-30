from enum import StrEnum

from .._base import XBase


class Flow(StrEnum):
    xtls = "xtls-rprx-vision"
    none = ""


class VlessClient(XBase):
    id: str
    level: int = 0
    email: str
    flow: Flow = Flow.xtls


class XVlessIn(XBase):
    clients: list[VlessClient]
    decryption: str
    fallbacks: ...
