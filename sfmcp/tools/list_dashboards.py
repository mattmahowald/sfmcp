from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..salesforce_client import SalesforceClient


class DashboardInfo(BaseModel):
    id: str
    title: str | None = None
    developerName: str | None = None
    folderName: str | None = None
    description: str | None = None
    ownerId: str | None = None
    lastViewedDate: str | None = None
    lastReferencedDate: str | None = None


class ListDashboardsResult(BaseModel):
    dashboards: List[DashboardInfo]
    total_count: int = Field(..., description="Total number of dashboards")


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="salesforce_list_dashboards",
        description="Get list of all Salesforce dashboards with their folder and usage information",
    )
    async def list_salesforce_dashboards() -> ListDashboardsResult:
        """Get list of Salesforce dashboards"""
        sf = SalesforceClient.from_env()
        dashboards_data = await sf.list_dashboards()

        dashboards = []
        for dashboard_data in dashboards_data:
            dashboard_info = DashboardInfo(
                id=dashboard_data.get("id", ""),
                title=dashboard_data.get("title"),
                developerName=dashboard_data.get("developerName"),
                folderName=dashboard_data.get("folderName"),
                description=dashboard_data.get("description"),
                ownerId=dashboard_data.get("ownerId"),
                lastViewedDate=dashboard_data.get("lastViewedDate"),
                lastReferencedDate=dashboard_data.get("lastReferencedDate"),
            )
            dashboards.append(dashboard_info)

        return ListDashboardsResult(dashboards=dashboards, total_count=len(dashboards))