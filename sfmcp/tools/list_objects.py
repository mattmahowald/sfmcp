from __future__ import annotations
import asyncio
from typing import List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..salesforce_client import SalesforceClient


class ListObjectsResult(BaseModel):
    object_names: List[str] = Field(..., description="List of Salesforce object names")
    total_count: int = Field(..., description="Total number of objects")


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="salesforce.list_objects",
        description="Get list of all Salesforce object names (SObjects)"
    )
    def list_salesforce_objects() -> ListObjectsResult:
        """Get list of Salesforce object names"""

        async def get_objects():
            sf = SalesforceClient.from_env()
            object_names = await sf.list_objects()
            return ListObjectsResult(
                object_names=object_names,
                total_count=len(object_names)
            )

        return asyncio.run(get_objects())