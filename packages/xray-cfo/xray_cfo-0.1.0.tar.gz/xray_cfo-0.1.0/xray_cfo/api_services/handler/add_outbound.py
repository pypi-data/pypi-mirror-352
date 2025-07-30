from enum import StrEnum

from grpclib.exceptions import GRPCError

from xray_cfo.xray.app.proxyman.command import AddOutboundRequest, AddOutboundResponse

from .._base import BaseService


class OutProtocol(StrEnum):
    blackhole = "blackhole"
    freedom = "freedom"


class HandlerAddOutboundService(BaseService):

    async def _add_outbound(
        self, message: AddOutboundRequest
    ) -> AddOutboundResponse | None:
        try:
            return await self.handler_stub.add_outbound(message)
        except GRPCError as e:
            return None
