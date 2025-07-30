from pydantic import Field

from ._base import XBase


class LevelPolicy(XBase):
    handshake: int = 4
    conn_idle: int = Field(300, serialization_alias="connIdle")
    uplink_only: int = Field(2, serialization_alias="uplinkOnly")
    downlink_only: int = Field(5, serialization_alias="downlinkOnly")
    stats_user_Uplink: bool = Field(False, serialization_alias="statsUserUplink")
    stats_user_downlink: bool = Field(False, serialization_alias="statsUserDownlink")
    stats_user_online: bool = Field(False, serialization_alias="statsUserOnline")
    buffer_size: int = Field(10240, serialization_alias="statsInboundUplink")


class SystemPolicy(XBase):
    stats_inbound_uplink: bool = Field(False, serialization_alias="statsInboundUplink")
    stats_inbound_downlink: bool = Field(False, serialization_alias="statsInboundDownlink")
    stats_outbound_uplink: bool = Field(False, serialization_alias="statsOutboundUplink")
    stats_outbound_downlink: bool = Field(False, serialization_alias="statsOutboundDownlink")


class XPolicy(XBase):
    levels: dict[str, LevelPolicy]
    system: SystemPolicy
