from grpclib.exceptions import GRPCError

from xray_cfo.xray.app.router.command import (
    AddRuleRequest,
    GetBalancerInfoRequest,
    OverrideBalancerTargetRequest,
    RemoveRuleRequest,
    RoutingContext,
    TestRouteRequest,
)
from xray_cfo.xray.common.serial import TypedMessage

from .._base import BaseService


class RoutingService(BaseService):

    async def subscribe_routing_stats(self, *selectors: str):
        try:
            # return (
            #     await self.routing_stub.subscribe_routing_stats(
            #         SubscribeRoutingStatsRequest(
            #             field_selectors=list(selectors)
            #         )
            #     )
            # ).stat.value
            pass
        except GRPCError:
            return

    async def test_route(
        self, context: RoutingContext, *selectors: str, publish_result: bool = True
    ):
        try:
            return await self.routing_stub.test_route(
                TestRouteRequest(
                    routing_context=context,
                    field_selectors=list(selectors),
                    publish_result=publish_result,
                )
            )
        except GRPCError:
            return None

    async def get_balancer_info(self, tag: str):
        try:
            return (
                await self.routing_stub.get_balancer_info(
                    GetBalancerInfoRequest(
                        tag=tag,
                    )
                )
            ).balancer
        except GRPCError:
            return None

    async def override_balancer_target(self, balancer_tag: str, target: str):
        try:
            await self.routing_stub.override_balancer_target(
                OverrideBalancerTargetRequest(
                    balancer_tag=balancer_tag,
                    target=target,
                )
            )
            return True
        except GRPCError:
            return None

    async def add_rule(self, config: TypedMessage, should_append: bool = True):
        try:
            await self.routing_stub.add_rule(
                AddRuleRequest(
                    config=config,
                    should_append=should_append,
                )
            )
            return True
        except GRPCError as e:
            print(e.status)
            print(e.message)
            print(e.details)
            return None

    async def remove_rule(self, rule_tag: str):
        try:
            await self.routing_stub.remove_rule(
                RemoveRuleRequest(
                    rule_tag=rule_tag,
                )
            )
            return True
        except GRPCError:
            return None
