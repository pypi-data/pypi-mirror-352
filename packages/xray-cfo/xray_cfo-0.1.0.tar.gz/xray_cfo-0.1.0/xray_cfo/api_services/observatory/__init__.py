from grpclib.exceptions import GRPCError

from .._base import BaseService


class ObservatoryService(BaseService):

    async def get_outbound_status(self):

        try:
            return (await self.observatory_stub.get_outbound_status()).status.status
        except GRPCError:
            return None
