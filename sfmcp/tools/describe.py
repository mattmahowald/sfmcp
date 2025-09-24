from __future__ import annotations
from typing import Any, List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
# from ..salesforce_client import SalesforceClient

class DescribeArgs(BaseModel):
    object_api_name: str = Field(..., description="SObject API name, e.g., Account")

class FieldInfo(BaseModel):
    name: str
    type: str
    label: str | None = None
    nillable: bool | None = None
    picklistValues: List[str] | None = None

class DescribeResult(BaseModel):
    object_api_name: str
    fields: List[FieldInfo]

def register(mcp: FastMCP) -> None:
    @mcp.tool(name="salesforce.describe", description="Describe an SObject (stub)")
    def describe_object(args: DescribeArgs) -> DescribeResult:
        # Wire to SalesforceClient.describe(...) when available
        # meta = SalesforceClient.from_env().describe(args.object_api_name)
        # fields = [...]
        return DescribeResult(object_api_name=args.object_api_name, fields=[])
