from typing import TYPE_CHECKING

from xray_cfo.xray.app.stats.command import StatsServiceStub
from xray_cfo.xray.core.app.observatory.command import ObservatoryServiceStub
from xray_cfo.xray.transport.internet.grpc.encoding import GrpcServiceStub

if TYPE_CHECKING:
    from grpclib.client import Channel

from xray_cfo.xray.app.log.command import LoggerServiceStub
from xray_cfo.xray.app.proxyman.command import HandlerServiceStub
from xray_cfo.xray.app.router.command import RoutingServiceStub


class BaseService:
    _channel: "Channel"

    def __init__(self):
        self.grpc_stub = GrpcServiceStub(self._channel)
        self.handler_stub = HandlerServiceStub(self._channel)
        self.logger_stub = LoggerServiceStub(self._channel)
        self.observatory_stub = ObservatoryServiceStub(self._channel)
        self.routing_stub = RoutingServiceStub(self._channel)
        self.stats_stub = StatsServiceStub(self._channel)
