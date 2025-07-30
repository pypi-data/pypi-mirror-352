from grpclib.exceptions import GRPCError

from .._base import BaseService


class HandlerListBoundService(BaseService):

    async def list_inbounds(self):
        try:
            return (await self.handler_stub.list_inbounds()).inbounds
        except GRPCError:
            return None

    async def list_outbounds(self):
        try:
            return (await self.handler_stub.list_outbounds()).outbounds
        except GRPCError:
            return None
