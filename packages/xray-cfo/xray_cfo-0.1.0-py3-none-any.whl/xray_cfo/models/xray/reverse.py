from ._base import XBase


class Bridge(XBase):
    tag: str
    domain: str


class Portal(XBase):
    tag: str
    domain: str


class XReverse(XBase):
    bridges: list[Bridge] | None = None
    portals: list[Portal] | None = None
