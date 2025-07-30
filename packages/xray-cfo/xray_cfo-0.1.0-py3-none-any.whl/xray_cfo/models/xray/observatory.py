from pydantic import Field

from ._base import XBase


class XObservatory(XBase):
    subject_selector: list[str] = Field(serialization_alias="subjectSelector")
    probe_url: str = Field(serialization_alias="probeUrl")
    probe_interval: str = Field("100s", serialization_alias="probeInterval")
    enable_concurrency: bool = Field(False, serialization_alias="enableConcurrency")


class PingConfig(XBase):
    destination: str
    connectivity: str = ""
    interval: str = "1h"
    sampling: int = 5
    timeout: str = "30s"


class XBurstObservatory(XBase):
    subject_selector: list[str] = Field(serialization_alias="subjectSelector")
    ping_config: PingConfig = Field(serialization_alias="pingConfig")
