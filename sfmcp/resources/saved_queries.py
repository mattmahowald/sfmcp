from __future__ import annotations
from typing import Iterable, Tuple
from mcp.server.fastmcp import FastMCP

def _saved_queries() -> Iterable[Tuple[str, str]]:
    yield ("recent_opportunities",
           "SELECT Id, Name, StageName, Amount FROM Opportunity ORDER BY LastModifiedDate DESC LIMIT 25")
    yield ("active_users",
           "SELECT Id, Name, Email FROM User WHERE IsActive = true")

def register(mcp: FastMCP) -> None:
    @mcp.resource.list()
    def list_resources():
        return [
            mcp.resource.item(
                uri=f"res://query/{name}",
                name=name,
                mimeType="text/plain",
                description="Saved SOQL query",
            )
            for name, _ in _saved_queries()
        ]

    @mcp.resource.read()
    def read_resource(uri: str):
        prefix = "res://query/"
        if not uri.startswith(prefix):
            raise ValueError("Unknown resource")
        name = uri[len(prefix):]
        for qname, content in _saved_queries():
            if qname == name:
                return {"contents": [{"uri": uri, "mimeType": "text/plain", "text": content}]}
        raise ValueError("Resource not found")
