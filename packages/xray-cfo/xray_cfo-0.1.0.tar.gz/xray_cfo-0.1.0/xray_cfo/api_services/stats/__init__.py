from grpclib.exceptions import GRPCError

from xray_cfo.xray.app.stats.command import GetStatsRequest, QueryStatsRequest

from .._base import BaseService


class StatsAPIService(BaseService):

    async def get_client_download_traffic(self, email: str, reset: bool = False):
        try:
            return (
                await self.stats_stub.get_stats(
                    GetStatsRequest(
                        name=f"user>>>{email}>>>traffic>>>downlink", reset=reset
                    )
                )
            ).stat.value
        except GRPCError:
            return None

    async def get_client_upload_traffic(self, email: str, reset=False):
        try:
            return (
                await self.stats_stub.get_stats(
                    GetStatsRequest(
                        name=f"user>>>{email}>>>traffic>>>uplink", reset=reset
                    )
                )
            ).stat.value
        except GRPCError:
            return None

    async def get_inbound_download_traffic(self, tag: str, reset=False):
        try:
            return (
                await self.stats_stub.get_stats(
                    GetStatsRequest(
                        name=f"inbound>>>{tag}>>>traffic>>>downlink", reset=reset
                    )
                )
            ).stat.value
        except GRPCError:
            return None

    async def get_inbound_upload_traffic(self, tag: str, reset=False):
        try:
            return (
                await self.stats_stub.get_stats(
                    GetStatsRequest(
                        name=f"inbound>>>{tag}>>>traffic>>>uplink", reset=reset
                    )
                )
            ).stat.value
        except GRPCError:
            return None

    async def stats_online(self, user: str, reset: bool = False):
        try:
            return (
                await self.stats_stub.get_stats_online(
                    GetStatsRequest(name=f"user>>>{user}>>>online", reset=reset)
                )
            ).stat.value
        except GRPCError:
            return None

    async def stats_query(self, pattern: str, reset: bool = False):
        try:
            return (
                await self.stats_stub.query_stats(
                    QueryStatsRequest(pattern=pattern, reset=reset)
                )
            ).stat.value
        except GRPCError:
            return None

    async def get_sys_stats(self):
        try:
            sys_stats = await self.stats_stub.get_sys_stats()

            # TODO: add Model to return

            return sys_stats
        except GRPCError:
            return None

    async def get_stats_online_ip_list(self, name: str, reset: bool = False):
        try:
            return (
                await self.stats_stub.get_stats_online_ip_list(
                    GetStatsRequest(name=name, reset=reset)
                )
            ).ips
        except GRPCError:
            return None
