from enum import StrEnum

from pydantic import Field

from .._base import XBase
from .grpc import XGRPCSettings
from .httpupgrade import XHttpUpgradeSettings
from .kcp import XKCPSettings
from .raw import XRawSettings
from .reality import XRealitySettingsIN, XRealitySettingsOUT
from .socopt import Sockopt
from .tls import XTLSSettings
from .ws import XWebSocketSettings
from .xhttp import XXHttpSettings


class StreamNetwork(StrEnum):
    raw = "raw"
    xhttp = "xhttp"
    kcp = "kcp"
    grpc = "grpc"
    ws = "ws"
    httpupgrade = "httpupgrade"


class Security(StrEnum):
    none = "none"
    tls = "tls"
    reality = "reality"


class XStreamSettings(XBase):
    network: StreamNetwork = StreamNetwork.raw
    security: Security = Security.none
    tls_settings: XTLSSettings | None = Field(None, serialization_alias="tlsSettings")
    reality_settings: XRealitySettingsIN | XRealitySettingsOUT | None = Field(
        None, serialization_alias="realitySettings"
    )
    raw_settings: XRawSettings | None = Field(None, serialization_alias="rawSettings")
    xhttp_settings: XXHttpSettings | None = Field(
        None, serialization_alias="xhttpSettings"
    )
    kcp_settings: XKCPSettings | None = Field(None, serialization_alias="kcpSettings")
    grpc_settings: XGRPCSettings | None = Field(
        None, serialization_alias="grpcSettings"
    )
    ws_settings: XWebSocketSettings | None = Field(
        None, serialization_alias="wsSettings"
    )
    httpupgrade_settings: XHttpUpgradeSettings | None = Field(
        None, serialization_alias="httpupgradeSettings"
    )
    sockopt: Sockopt | None = Field(None)
