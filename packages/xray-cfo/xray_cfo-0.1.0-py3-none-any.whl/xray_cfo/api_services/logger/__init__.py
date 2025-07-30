from grpclib.exceptions import GRPCError

from xray_cfo.xray.app.log.command import RestartLoggerRequest

from .._base import BaseService


class LoggerService(BaseService):

    async def restart_logger(self):
        try:
            await self.logger_stub.restart_logger(RestartLoggerRequest())
        except GRPCError:
            return
