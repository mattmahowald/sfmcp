from __future__ import annotations
import asyncio
from typing import Any, List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from ..salesforce_client import SalesforceClient


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
    @mcp.tool(
        name="salesforce.describe",
        description="Describe an SObject and return field information",
    )
    def describe_object(args: DescribeArgs) -> DescribeResult:

        async def get_describe():
            sf = SalesforceClient.from_env()
            describe_data = await sf.describe_object(args.object_api_name)

            # Extract field information
            fields = []
            for field_data in describe_data.get("fields", []):
                # Extract picklist values if present
                picklist_values = None
                if (
                    field_data.get("type") == "picklist"
                    and "picklistValues" in field_data
                ):
                    picklist_values = [
                        pv.get("value")
                        for pv in field_data["picklistValues"]
                        if pv.get("active")
                    ]

                field_info = FieldInfo(
                    name=field_data.get("name", ""),
                    type=field_data.get("type", ""),
                    label=field_data.get("label"),
                    nillable=field_data.get("nillable"),
                    picklistValues=picklist_values,
                )
                fields.append(field_info)

            return DescribeResult(object_api_name=args.object_api_name, fields=fields)

        return asyncio.run(get_describe())
