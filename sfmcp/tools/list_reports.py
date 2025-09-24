from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..salesforce_client import SalesforceClient


class ReportInfo(BaseModel):
    id: str
    name: str | None = None
    developerName: str | None = None
    format: str | None = None
    folderName: str | None = None
    description: str | None = None
    ownerId: str | None = None
    lastRunDate: str | None = None
    lastViewedDate: str | None = None
    lastReferencedDate: str | None = None


class ListReportsResult(BaseModel):
    reports: List[ReportInfo]
    total_count: int = Field(..., description="Total number of reports")


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="salesforce_list_reports",
        description="Get list of all Salesforce reports with their folder and usage information",
    )
    async def list_salesforce_reports() -> ListReportsResult:
        """Get list of Salesforce reports"""
        sf = SalesforceClient.from_env()
        reports_data = await sf.list_reports()

        reports = []
        for report_data in reports_data:
            report_info = ReportInfo(
                id=report_data.get("id", ""),
                name=report_data.get("name"),
                developerName=report_data.get("developerName"),
                format=report_data.get("format"),
                folderName=report_data.get("folderName"),
                description=report_data.get("description"),
                ownerId=report_data.get("ownerId"),
                lastRunDate=report_data.get("lastRunDate"),
                lastViewedDate=report_data.get("lastViewedDate"),
                lastReferencedDate=report_data.get("lastReferencedDate"),
            )
            reports.append(report_info)

        return ListReportsResult(reports=reports, total_count=len(reports))