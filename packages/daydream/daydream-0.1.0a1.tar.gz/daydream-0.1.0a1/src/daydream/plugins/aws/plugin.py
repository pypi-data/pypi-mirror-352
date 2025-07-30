from collections.abc import AsyncGenerator
from typing import Any, Literal

import anyio
from aioboto3 import Session

from daydream.knowledge import Graph
from daydream.plugins import Plugin
from daydream.plugins.aws.nodes.aws_alb_target_group import AwsAlbTargetGroup
from daydream.plugins.aws.nodes.aws_application_load_balancer import (
    AwsApplicationLoadBalancer,
)
from daydream.plugins.aws.nodes.aws_classic_load_balancer import AwsClassicLoadBalancer
from daydream.plugins.aws.nodes.aws_ebs_volume import AwsEbsVolume
from daydream.plugins.aws.nodes.aws_ec2_instance import AwsEc2Instance
from daydream.plugins.aws.nodes.aws_rds_database import AwsRdsDatabase
from daydream.plugins.aws.utils import (
    list_accessible_regions_for_service,
    swallow_boto_client_access_errors,
)
from daydream.plugins.mixins import KnowledgeGraphMixin
from daydream.utils import print


class AwsPlugin(Plugin, KnowledgeGraphMixin):
    def __init__(self, **settings: Any) -> None:
        super().__init__(**settings)
        self._session = Session()

    @property
    def session(self) -> Session:
        return self._session

    async def _ensure_session(self) -> None:
        async with self.session.client("sts") as client:
            try:
                await client.get_caller_identity()
            except Exception as e:
                print(f"Error using session to call STS GetCallerIdentity: {e}")
                raise

    async def populate_graph(self, graph: Graph) -> None:
        await self._ensure_session()
        async with anyio.create_task_group() as tg:
            tg.start_soon(self.populate_rds_databases, graph)
            tg.start_soon(self.populate_ec2_instances, graph)
            tg.start_soon(self.populate_classic_load_balancers, graph)
            tg.start_soon(self.populate_application_load_balancers, graph)
            tg.start_soon(self.populate_alb_target_groups, graph)
            tg.start_soon(self.populate_ebs_volumes, graph)

    async def populate_rds_databases(self, graph: Graph) -> None:
        async with anyio.create_task_group() as tg:
            for region in await list_accessible_regions_for_service(self.session, "rds"):
                tg.start_soon(self._populate_rds_databases_in_region, graph, region)

    async def _populate_rds_databases_in_region(self, graph: Graph, region: str) -> None:
        print(f"Populating RDS databases from {region}")

        rds_database_count = 0
        async for page in self._paginate("rds", "describe_db_instances", region):
            for instance in page["DBInstances"]:
                await graph.add_node(
                    AwsRdsDatabase(
                        node_id=instance["DBInstanceArn"],
                        raw_data=instance,
                        _graph=graph,
                    )
                )
                rds_database_count += 1

        print(f"Initialized {rds_database_count} RDS databases for {region}")

    async def populate_ec2_instances(self, graph: Graph) -> None:
        async with anyio.create_task_group() as tg:
            for region in await list_accessible_regions_for_service(self.session, "ec2"):
                tg.start_soon(self._populate_ec2_instances_in_region, graph, region)

    async def _populate_ec2_instances_in_region(self, graph: Graph, region: str) -> None:
        print(f"Populating EC2 instances from {region}")

        ec2_instance_count = 0
        async for page in self._paginate("ec2", "describe_instances", region):
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    await graph.add_node(
                        AwsEc2Instance(
                            node_id=instance["InstanceId"],
                            raw_data=instance,
                            _graph=graph,
                        )
                    )
                    ec2_instance_count += 1

        print(f"Initialized {ec2_instance_count} EC2 instances for {region}")

    async def populate_classic_load_balancers(self, graph: Graph) -> None:
        async with anyio.create_task_group() as tg:
            for region in await list_accessible_regions_for_service(self.session, "elb"):
                tg.start_soon(self._populate_classic_load_balancers_in_region, graph, region)

    async def _populate_classic_load_balancers_in_region(self, graph: Graph, region: str) -> None:
        print(f"Populating classic load balancers from {region}")

        elb_count = 0
        async for page in self._paginate("elb", "describe_load_balancers", region):
            for balancer in page["LoadBalancerDescriptions"]:
                await graph.add_node(
                    AwsClassicLoadBalancer(
                        node_id=balancer["LoadBalancerName"],
                        raw_data=balancer,
                        _graph=graph,
                    )
                )
                elb_count += 1

        print(f"Initialized {elb_count} classic load balancers for {region}")

    async def populate_application_load_balancers(self, graph: Graph) -> None:
        async with anyio.create_task_group() as tg:
            for region in await list_accessible_regions_for_service(self.session, "elbv2"):
                tg.start_soon(self._populate_application_load_balancers_in_region, graph, region)

    async def _populate_application_load_balancers_in_region(
        self, graph: Graph, region: str
    ) -> None:
        print(f"Populating application load balancers from {region}")

        alb_count = 0
        async for page in self._paginate("elbv2", "describe_load_balancers", region):
            for balancer in page["LoadBalancers"]:
                await graph.add_node(
                    AwsApplicationLoadBalancer(
                        node_id=balancer["LoadBalancerArn"],
                        raw_data=balancer,
                        _graph=graph,
                    )
                )
                alb_count += 1

        print(f"Initialized {alb_count} application load balancers for {region}")

    async def populate_alb_target_groups(self, graph: Graph) -> None:
        async with anyio.create_task_group() as tg:
            for region in await list_accessible_regions_for_service(self.session, "elbv2"):
                tg.start_soon(self._populate_alb_target_groups_in_region, graph, region)

    async def _populate_alb_target_groups_in_region(self, graph: Graph, region: str) -> None:
        print(f"Populating ALB target groups from {region}")

        alb_target_group_count = 0
        async for page in self._paginate("elbv2", "describe_target_groups", region):
            for target_group in page["TargetGroups"]:
                await graph.add_node(
                    AwsAlbTargetGroup(
                        node_id=target_group["TargetGroupArn"],
                        raw_data=target_group,
                        _graph=graph,
                    )
                )
                alb_target_group_count += 1

        print(f"Initialized {alb_target_group_count} ALB target groups for {region}")

    async def populate_ebs_volumes(self, graph: Graph) -> None:
        async with anyio.create_task_group() as tg:
            for region in await list_accessible_regions_for_service(self.session, "ec2"):
                tg.start_soon(self._populate_ebs_volumes_in_region, graph, region)

    async def _populate_ebs_volumes_in_region(self, graph: Graph, region: str) -> None:
        print(f"Populating EBS volumes from {region}")

        ebs_volume_count = 0
        async for page in self._paginate("ec2", "describe_volumes", region):
            for volume in page["Volumes"]:
                await graph.add_node(
                    AwsEbsVolume(
                        node_id=volume["VolumeId"],
                        raw_data=volume,
                        _graph=graph,
                    )
                )
                ebs_volume_count += 1

        print(f"Initialized {ebs_volume_count} EBS volumes for {region}")

    async def _paginate(
        self,
        service_name: Literal["ec2", "elb", "elbv2", "rds"],
        action: str,
        region: str,
    ) -> AsyncGenerator[dict, None]:
        async with (
            swallow_boto_client_access_errors(service_name=service_name, region=region),
            self.session.client(service_name, region_name=region) as client,
        ):
            paginator = client.get_paginator(action)
            async for page in paginator.paginate():
                yield page
