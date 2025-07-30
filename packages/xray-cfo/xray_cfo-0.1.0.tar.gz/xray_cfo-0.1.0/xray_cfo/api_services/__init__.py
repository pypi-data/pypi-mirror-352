from xray_cfo.api_services.grpc import GRPCService
from xray_cfo.api_services.handler import HandlerService
from xray_cfo.api_services.logger import LoggerService
from xray_cfo.api_services.observatory import ObservatoryService
from xray_cfo.api_services.routing import RoutingService
from xray_cfo.api_services.stats import StatsAPIService


class APIService(
    StatsAPIService,
    LoggerService,
    ObservatoryService,
    GRPCService,
    RoutingService,
    HandlerService,
):
    pass
