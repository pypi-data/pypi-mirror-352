from grpclib.exceptions import GRPCError

from xray_cfo.common import utils
from xray_cfo.xray.app.proxyman.command import AddUserOperation, AlterInboundRequest
from xray_cfo.xray.common.protocol import User
from xray_cfo.xray.proxy import shadowsocks, vless
from xray_cfo.xray.proxy.shadowsocks import CipherType

from .._base import BaseService


class HandlerAddClientService(BaseService):

    async def add_client_vless(
        self,
        inbound_tag: str,
        user_id: str,
        email: str,
        level: int = 0,
        flow: str = "none",
        encryption: str = "none",
    ):
        try:
            await self.handler_stub.alter_inbound(
                AlterInboundRequest(
                    tag=inbound_tag,
                    operation=utils.to_typed_message(
                        AddUserOperation(
                            user=User(
                                email=email,
                                level=level,
                                account=utils.to_typed_message(
                                    vless.Account(
                                        id=user_id,
                                        flow=flow,
                                        encryption=encryption,
                                    )
                                ),
                            )
                        )
                    ),
                )
            )
            return user_id
        except GRPCError:
            return None

    async def add_client_ss(
        self,
        inbound_tag: str,
        user_id: str,
        email: str,
        level: int = 0,
    ):
        try:
            await self.handler_stub.alter_inbound(
                AlterInboundRequest(
                    tag=inbound_tag,
                    operation=utils.to_typed_message(
                        AddUserOperation(
                            user=User(
                                email=email,
                                level=level,
                                account=utils.to_typed_message(
                                    shadowsocks.Account(
                                        password=user_id,
                                        cipher_type=CipherType.CHACHA20_POLY1305,
                                        iv_check=True,
                                    )
                                ),
                            )
                        )
                    ),
                )
            )
            return user_id
        except GRPCError:
            return None

    async def add_client_wg(self, inbound_tag: str):

        try:
            inbounds_data = await self.handler_stub.list_inbounds()
            for inbound in inbounds_data.inbounds:
                if inbound_tag == inbound.tag:
                    selected_inbound = inbound
                    break
            else:
                return

            # TODO(CFO): need edit_inbound and add peer

        except:
            return
