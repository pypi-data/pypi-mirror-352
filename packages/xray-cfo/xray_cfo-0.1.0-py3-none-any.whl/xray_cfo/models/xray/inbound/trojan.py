from .._base import XBase


class TrojanClient(XBase):
    user: str
    password: str
    level: int = 0


class XTrojanIn(XBase):
    clients: list[TrojanClient]
    fallbacks: ...
