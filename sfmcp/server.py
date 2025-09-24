from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServer
from .config.logging import configure_logging
from .config.settings import settings

# submodules
from .tools import query as tool_query
from .tools import describe as tool_describe
from .tools import list_objects as tool_list_objects
from .resources import saved_queries as res_saved_queries
from .prompts import opps_by_stage as prm_opps_by_stage

mcp = FastMCP("sfmcp")

def _register_all() -> None:
    tool_query.register(mcp)
    tool_describe.register(mcp)
    tool_list_objects.register(mcp)
    res_saved_queries.register(mcp)
    prm_opps_by_stage.register(mcp)

def run_stdio() -> None:
    configure_logging()
    _register_all()
    mcp.run_stdio()

def run_http() -> None:
    configure_logging()
    _register_all()
    app = SseServer(mcp).fastapi
    import uvicorn
    uvicorn.run(app, host=settings.http_host, port=settings.http_port)
