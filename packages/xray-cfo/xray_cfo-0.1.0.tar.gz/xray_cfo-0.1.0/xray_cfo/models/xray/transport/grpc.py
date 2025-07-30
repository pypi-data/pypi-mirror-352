from pydantic import Field

from .._base import XBase


class XGRPCSettings(XBase):
    authority: str | None = None
    service_name: str = Field("/", serialization_alias="serviceName")
    multi_mode: bool = Field(False, serialization_alias="multiMode")
    user_agent: str | None = None
    idle_timeout: int | None = None
    health_check_timeout: int | None = None
    permit_without_stream: bool | None = None
    initial_windows_size:  int | None = None
