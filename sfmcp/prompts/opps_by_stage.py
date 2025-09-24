from __future__ import annotations
from mcp.server.fastmcp import FastMCP, Prompt, PromptMessage


def register(mcp: FastMCP) -> None:
    @mcp.prompt.list()
    def list_prompts():
        return [
            Prompt(
                name="opps_by_stage",
                description="Generate a SOQL to list opportunities by a given StageName",
            )
        ]

    @mcp.prompt.get()
    def get_prompt(name: str, arguments: dict[str, str] | None = None):
        if name != "opps_by_stage":
            raise ValueError("Unknown prompt")
        stage = (arguments or {}).get("stage", "Prospecting")
        content = (
            "SELECT Id, Name, Amount "
            f"FROM Opportunity WHERE StageName = '{stage}' "
            "ORDER BY Amount DESC LIMIT 50"
        )
        return [PromptMessage(role="user", content=content)]
