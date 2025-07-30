import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aioboto3 import Session
from botocore.exceptions import ClientError


async def list_accessible_regions_for_service(session: Session, service_name: str) -> list[str]:
    """Return a list of regions that the current credentials can access."""

    async def _check_region(region: str) -> tuple[str, bool]:
        """Attempt to call an API in the given region. Return True if accessible."""
        try:
            async with session.client("sts", region_name=region) as client:
                await client.get_caller_identity()
            return region, True
        except ClientError:
            return region, False

    # Now, check access to each region (concurrently)
    results = await asyncio.gather(
        *(_check_region(region) for region in await session.get_available_regions(service_name))
    )

    return [region for region, success in results if success]


@asynccontextmanager
async def swallow_boto_client_access_errors(
    service_name: str | None = None, region: str | None = None
) -> AsyncIterator[None]:
    try:
        yield
    except ClientError as e:
        err = e.response.get("Error", {})
        error_code = err.get("Code", None)
        error_msg = err.get("Message", "Unknown Message")
        if error_code in [
            "AccessDenied",
            "AccessDeniedException",
            "AuthorizationError",
            "UnauthorizedOperation",
        ]:
            print(
                f"Ignoring access denied ({error_code}) for {f'{service_name}.' if service_name else ''}{e.operation_name}{f' in {region}' if region else ''}: {error_msg}",
                file=sys.stderr,
            )
            return
        raise
