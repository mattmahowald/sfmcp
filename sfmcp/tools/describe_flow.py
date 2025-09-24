from __future__ import annotations
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..salesforce_client import SalesforceClient


class DescribeFlowArgs(BaseModel):
    flow_developer_name: str = Field(..., description="Flow developer name (e.g., Contact_Last_Reply_Date)")


class DescribeFlowResult(BaseModel):
    flowDeveloperName: str
    flowContent: str
    contentLength: int
    filePath: str


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="salesforce_describe_flow",
        description="Retrieve the full XML metadata for a specific Salesforce flow by developer name",
    )
    async def describe_salesforce_flow(args: DescribeFlowArgs) -> DescribeFlowResult:
        """Get the complete flow definition XML by retrieving it from Salesforce"""
        sf = SalesforceClient.from_env()
        flow_data = await sf.describe_flow(args.flow_developer_name)

        return DescribeFlowResult(
            flowDeveloperName=flow_data["flowDeveloperName"],
            flowContent=flow_data["flowContent"],
            contentLength=flow_data["contentLength"],
            filePath=flow_data["filePath"],
        )