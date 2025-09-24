from __future__ import annotations
import logging
from mcp.server.fastmcp import FastMCP
from .config.logging import configure_logging
from .config.settings import settings

logger = logging.getLogger("sfmcp.server")

# submodules
from .tools import query as tool_query
from .tools import describe as tool_describe
from .tools import list_objects as tool_list_objects
from .tools import list_flows as tool_list_flows
from .tools import list_reports as tool_list_reports
from .tools import list_dashboards as tool_list_dashboards
from .tools import describe_flow as tool_describe_flow
# from .resources import saved_queries as res_saved_queries
# from .prompts import opps_by_stage as prm_opps_by_stage

mcp = FastMCP("sfmcp")


def _register_all() -> None:
    tool_query.register(mcp)
    tool_describe.register(mcp)
    tool_list_objects.register(mcp)
    tool_list_flows.register(mcp)
    tool_list_reports.register(mcp)
    tool_list_dashboards.register(mcp)
    tool_describe_flow.register(mcp)
    # res_saved_queries.register(mcp)
    # prm_opps_by_stage.register(mcp)


def run_stdio() -> None:
    # Disable logging for STDIO mode to avoid interfering with MCP protocol
    configure_logging(level=logging.CRITICAL)
    _register_all()
    mcp.run()


def run_http() -> None:
    configure_logging()
    _register_all()

    # FastMCP provides direct HTTP support
    import asyncio
    logger.info(f"Starting SFMCP HTTP server at {settings.http_host}:{settings.http_port}")
    asyncio.run(mcp.run_sse_async())
