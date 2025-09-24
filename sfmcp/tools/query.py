from __future__ import annotations
import asyncio
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..salesforce_client import SalesforceClient


class QueryArgs(BaseModel):
    soql: str = Field(..., description="SOQL query string")
    max_records: int | None = Field(None, ge=1, le=50000)


class QueryResult(BaseModel):
    total_size: int
    records: List[Dict[str, Any]]


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="salesforce_query", description="Run a SOQL query and return JSON rows"
    )
    async def salesforce_query(args: QueryArgs) -> QueryResult:
        sf = SalesforceClient.from_env()
        rows = await sf.run_soql(args.soql)
        if args.max_records is not None:
            rows = rows[: args.max_records]
        return QueryResult(total_size=len(rows), records=rows)
