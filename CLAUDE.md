# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

You are a thoughtful and careful but autonomous coding agent. You focus heavily on
clarifying the path and direction with the user to get you on a path that will allow
you to operate autonomously.

1. Languages
   • Default to Python.
   • When using JavaScript, default to TypeScript.
2. Python Standards
   • Always use Poetry for dependency management.
   • Always enable mypy type checking.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Project Overview

This is a Salesforce MCP (Model Context Protocol) server that provides tools for querying and interacting with Salesforce data through the `sf` command line tool. It's built using FastMCP and can run in both STDIO and HTTP modes.

## Architecture

The codebase follows a modular structure:

- **`sfmcp/server.py`**: Main server entry point that registers all tools, resources, and prompts
- **`sfmcp/tools/`**: MCP tool implementations (query, describe)
- **`sfmcp/resources/`**: MCP resource implementations (saved_queries)
- **`sfmcp/prompts/`**: MCP prompt implementations (opps_by_stage)
- **`sfmcp/salesforce_client.py`**: Salesforce API client abstraction (currently a stub)
- **`sfmcp/config/`**: Configuration and logging setup

The server uses a registration pattern where all tools, resources, and prompts are registered through their respective `register(mcp)` functions called from `_register_all()`.

## Development Commands

### Setup
```bash
poetry install
```

### Running the Server
STDIO mode (for MCP clients):
```bash
poetry run sfmcp-stdio
# or
./scripts/run_stdio.sh
```

HTTP mode (for development/testing):
```bash
poetry run sfmcp-http
# or
./scripts/run_http.sh
```

### Code Quality
```bash
# Type checking
poetry run mypy sfmcp/

# Linting
poetry run ruff check sfmcp/

# Formatting
poetry run ruff format sfmcp/
```

### Testing
```bash
poetry run pytest tests/
```

## Configuration

The server uses environment-based configuration:
- `SFMCP_HTTP_HOST`: HTTP server host (default: 127.0.0.1)
- `SFMCP_HTTP_PORT`: HTTP server port (default: 3333)
- Salesforce credentials via `sf_instance_url` and `sf_access_token` settings

## Key Dependencies

- **mcp**: Model Context Protocol server framework
- **fastapi/uvicorn**: HTTP server for development mode
- **pydantic**: Data validation and serialization
- **mypy**: Static type checking (strict mode enabled)
- **ruff**: Fast Python linter and formatter

## Gotchas

### MCP Tool Name Validation
**Issue:** Claude Desktop validates MCP tool names with pattern `^[a-zA-Z0-9_-]{1,64}$`

**Problem:** Tool names with periods (e.g., `salesforce.query`) will cause validation errors:
```
tools.93.FrontendRometeMcpToolDefinition.name: String should match pattern '^[a-zA-Z0-9_-]{1,64}$'
```

**Solution:** Use underscores instead of periods in tool names:
- ❌ `salesforce.query`
- ✅ `salesforce_query`

### STDIO Logging Interference
**Issue:** Any logging output during STDIO mode interferes with MCP protocol communication.

**Problem:** Causes `BrokenPipeError: [Errno 32] Broken pipe` and connection failures.

**Solution:** Disable logging for STDIO mode:
```python
def run_stdio() -> None:
    configure_logging(level=logging.CRITICAL)  # Suppress all logs
    mcp.run()
```

### Async Event Loop Conflicts
**Issue:** MCP server already runs in an async event loop.

**Problem:** Using `asyncio.run()` inside MCP tools causes:
```
Error executing tool: asyncio.run() cannot be called from a running event loop
```

**Solution:** Make MCP tool functions directly async:
```python
# ❌ Wrong - creates nested event loop
@mcp.tool()
def my_tool():
    return asyncio.run(async_function())

# ✅ Correct - tool function is async
@mcp.tool()
async def my_tool():
    return await async_function()
```