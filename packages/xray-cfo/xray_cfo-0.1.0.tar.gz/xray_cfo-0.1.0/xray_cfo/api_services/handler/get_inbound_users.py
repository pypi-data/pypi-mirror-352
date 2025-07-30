from grpclib.exceptions import GRPCError

from xray_cfo.api_services._base import BaseService
from xray_cfo.xray.app.proxyman.command import GetInboundUserRequest


class HandlerGetInboundUsersService(BaseService):

    async def get_inbound_users(self, tag: str, email: str):
        try:
            return (
                await self.handler_stub.get_inbound_users(
                    GetInboundUserRequest(tag=tag, email=email)
                )
            ).users
        except GRPCError:
            return None

    async def get_inbound_users_count(self, tag: str, email: str):
        try:
            return (
                await self.handler_stub.get_inbound_users_count(
                    GetInboundUserRequest(tag=tag, email=email)
                )
            ).count
        except GRPCError:
            return None
