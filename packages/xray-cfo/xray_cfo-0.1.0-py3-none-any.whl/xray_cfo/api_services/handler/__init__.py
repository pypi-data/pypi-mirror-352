from xray_cfo.api_services.handler.add_client import HandlerAddClientService
from xray_cfo.api_services.handler.add_inbound import HandlerAddInboundService
from xray_cfo.api_services.handler.add_outbound import HandlerAddOutboundService
from xray_cfo.api_services.handler.get_inbound_users import HandlerGetInboundUsersService
from xray_cfo.api_services.handler.list_bound import HandlerListBoundService
from xray_cfo.api_services.handler.remove_bound import HandlerRemoveBoundService
from xray_cfo.api_services.handler.remove_client import HandlerRemoveClientService


class HandlerService(
    HandlerGetInboundUsersService,
    HandlerAddClientService,
    HandlerListBoundService,
    HandlerRemoveBoundService,
    HandlerAddOutboundService,
    HandlerAddInboundService,
    HandlerRemoveClientService,
): ...
