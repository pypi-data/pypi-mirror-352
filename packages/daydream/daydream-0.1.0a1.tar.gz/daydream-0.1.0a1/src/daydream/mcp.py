import os
import signal
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import anyio
from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict

from daydream.config import Config, get_config_dir, load_config
from daydream.knowledge import Graph
from daydream.plugins import PluginManager
from daydream.plugins.mixins.mcp import McpServerMixin
from daydream.utils import print


class Context(BaseModel, extra="allow"):
    """Context for the MCP server."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    profile: str
    config: Config
    plugins: PluginManager
    mcp_server: FastMCP | None = None
    graph: Graph


def build_mcp_server(context: Context) -> FastMCP:
    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[Context]:
        """Initialize the application context and plugins."""
        yield context

    mcp = FastMCP("daydream", lifespan=lifespan, log_level="DEBUG", debug=True)

    for plugin in context.plugins:
        plugin.context = context

    for mcp_plugin in context.plugins.get_plugins_with_capability(McpServerMixin):
        mcp.mount(mcp_plugin.name, mcp_plugin.get_mcp_server())

    return mcp


async def start(profile: str, disable_sse: bool = False, disable_stdio: bool = False) -> None:
    """Start the MCP server.

    This function will start the MCP server with the specified transports.

    Args:
        disable_sse: If True, the SSE transport will be disabled.
        disable_stdio: If True, the stdio transport will be disabled.
    """
    # Register direct signal handlers for immediate exit
    signal.signal(signal.SIGINT, lambda *args: os._exit(0))
    signal.signal(signal.SIGTERM, lambda *args: os._exit(0))

    config = load_config(profile)
    plugins = PluginManager(config=config)
    context = Context(
        profile=profile,
        config=config,
        plugins=plugins,
        graph=Graph(get_config_dir(profile) / "graph.json"),
    )

    mcp = build_mcp_server(context)

    async with anyio.create_task_group() as tg:
        if not disable_stdio:
            tg.start_soon(mcp.run_stdio_async)
        if not disable_sse:
            tg.start_soon(mcp.run_sse_async)
            sse_url = f"http://{mcp.settings.host}:{mcp.settings.port}{mcp.settings.sse_path}"
            print(f"MCP server started on {sse_url}", transport="sse")

    print("MCP server stopped")
