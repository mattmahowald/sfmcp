from __future__ import annotations
from sfmcp.server import mcp, _register_all

def test_register_tools(env_setup: bool):
    _register_all()
    names = {t.name for t in mcp._tools}  # type: ignore[attr-defined]
    assert "salesforce.query" in names
    assert "salesforce.describe" in names
