from enum import StrEnum

from pydantic import BaseModel, Field

from ._base import XBase


class LogLevel(StrEnum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    none = "none"


class MaskAddress(StrEnum):
    quarter = "quarter"
    half = "half"
    full = "full"
    none = ""


class XLog(XBase):
    access: str = ""
    error: str = ""
    loglevel: LogLevel = LogLevel.none
    dns_log: bool = Field(False, serialization_alias="dnsLog")
    mask_address: MaskAddress = MaskAddress.none
