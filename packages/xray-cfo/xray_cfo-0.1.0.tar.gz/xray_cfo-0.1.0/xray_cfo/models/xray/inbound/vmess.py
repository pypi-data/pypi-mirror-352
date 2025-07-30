from enum import StrEnum

from .._base import XBase


class Flow(StrEnum):
    xtls = "xtls-rprx-vision"
    none = ""


class VmessClient(XBase):
    id: str
    level: int = 0
    email: str


class DefaultObject(XBase):
    level: int = 0


class DetourObject(XBase):
    to: str = 0


class XVmessIn(XBase):
    clients: list[VmessClient]
    default: DefaultObject
    detour: DetourObject
