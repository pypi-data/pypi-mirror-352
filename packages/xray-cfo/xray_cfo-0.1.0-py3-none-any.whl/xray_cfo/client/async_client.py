from types import TracebackType

from grpclib.client import Channel

from xray_cfo.api_services import APIService


class XrayClient(APIService):

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._channel = Channel(
            host=host,
            port=port,
        )
        super().__init__()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self):
        self._channel.close()
