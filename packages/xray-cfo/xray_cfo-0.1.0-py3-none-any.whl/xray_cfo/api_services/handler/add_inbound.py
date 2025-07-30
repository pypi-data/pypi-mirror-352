from grpclib.exceptions import GRPCError
from xray_cfo.xray.app.proxyman.command import AddInboundRequest

from .._base import BaseService


class HandlerAddInboundService(BaseService):
    async def _add_inbound(self, message: AddInboundRequest):
        try:
            return await self.handler_stub.add_inbound(message)
        except GRPCError:
            return None
