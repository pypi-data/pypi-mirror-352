from grpclib.exceptions import GRPCError

from xray_cfo.xray.app.proxyman.command import RemoveInboundRequest, RemoveOutboundRequest

from .._base import BaseService


class HandlerRemoveBoundService(BaseService):

    async def remove_inbound(self, tag: str):
        try:
            await self.handler_stub.remove_inbound(RemoveInboundRequest(tag=tag))
            return True
        except GRPCError:
            return None

    async def remove_outbound(self, tag: str):
        try:
            await self.handler_stub.remove_outbound(RemoveOutboundRequest(tag=tag))
            return True
        except GRPCError:
            return None
