from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..salesforce_client import SalesforceClient


class FlowInfo(BaseModel):
    id: str
    masterLabel: str | None = None
    status: str | None = None
    versionNumber: int | None = None
    developerName: str | None = None
    definitionId: str | None = None
    isActive: bool | None = None
    activeVersionId: str | None = None
    latestVersionId: str | None = None


class ListFlowsResult(BaseModel):
    flows: List[FlowInfo]
    total_count: int = Field(..., description="Total number of flows")


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="salesforce_list_flows",
        description="Get list of all Salesforce flows with their status and version information",
    )
    async def list_salesforce_flows() -> ListFlowsResult:
        """Get list of Salesforce flows"""
        sf = SalesforceClient.from_env()
        flows_data = await sf.list_flows()

        flows = []
        for flow_data in flows_data:
            flow_info = FlowInfo(
                id=flow_data.get("id", ""),
                masterLabel=flow_data.get("masterLabel"),
                status=flow_data.get("status"),
                versionNumber=flow_data.get("versionNumber"),
                developerName=flow_data.get("developerName"),
                definitionId=flow_data.get("definitionId"),
                isActive=flow_data.get("isActive"),
                activeVersionId=flow_data.get("activeVersionId"),
                latestVersionId=flow_data.get("latestVersionId"),
            )
            flows.append(flow_info)

        return ListFlowsResult(flows=flows, total_count=len(flows))