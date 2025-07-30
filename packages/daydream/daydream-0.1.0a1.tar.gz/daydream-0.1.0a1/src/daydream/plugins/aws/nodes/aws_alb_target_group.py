from daydream.plugins.aws.nodes.base import AwsNode


class AwsAlbTargetGroup(AwsNode):
    async def get_identifiers(self) -> list[str | None]:
        return [
            *await super().get_identifiers(),
            self.raw_data["TargetGroupArn"],
        ]

    async def get_reference_identifiers(
        self,
    ) -> list[str | None | tuple[str | None, str]]:
        return [
            *await super().get_reference_identifiers(),
            *((lb, "routes_requests_for") for lb in self.raw_data.get("LoadBalancerArns", [])),
            self.raw_data.get("VpcId"),
        ]
