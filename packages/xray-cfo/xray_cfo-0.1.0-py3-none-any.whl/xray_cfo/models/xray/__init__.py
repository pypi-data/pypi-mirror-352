from pydantic import Field

from xray_cfo.models.xray.api import XApi
from xray_cfo.models.xray.dns import XDns
from xray_cfo.models.xray.fake_dns import XFakeDns
from xray_cfo.models.xray.inbound import XInboundObject
from xray_cfo.models.xray.log import XLog
from xray_cfo.models.xray.metrics import XMetrics
from xray_cfo.models.xray.observatory import XBurstObservatory, XObservatory
from xray_cfo.models.xray.outbound import XOutboundObject
from xray_cfo.models.xray.policy import XPolicy
from xray_cfo.models.xray.reverse import XReverse
from xray_cfo.models.xray.routing import XRouting
from xray_cfo.models.xray.transport import XStreamSettings

from ._base import XBase


class XrayConfig(XBase):
    log: XLog | None = None
    api: XApi | None = None
    dns: XDns | None = None
    routing: XRouting | None = None
    policy: XPolicy | None = None
    inbounds: list[XInboundObject]
    outbounds: list[XOutboundObject]
    transport: XStreamSettings | None = None
    stats: dict | None = Field(default_factory=dict)
    reverse: XReverse | None = None
    fakedns: XFakeDns | list[XFakeDns] | None = None
    metrics: XMetrics | None = None
    observatory: XObservatory | None = None
    burst_observatory: XBurstObservatory | None = Field(
        None, serialization_alias="burstObservatory"
    )
