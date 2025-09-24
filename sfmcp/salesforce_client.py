from __future__ import annotations
import json
import asyncio
import logging
from typing import Any, Dict, List
from .config.settings import settings

logger = logging.getLogger("sfmcp.client")


class SalesforceClient:
    def __init__(self, *, instance_url: str, access_token: str):
        self._instance_url = instance_url
        self._access_token = access_token

    @classmethod
    def from_env(cls) -> "SalesforceClient":
        return cls(
            instance_url=settings.sf_instance_url,
            access_token=settings.sf_access_token,
        )

    async def _run_cli_command(self, command: List[str]) -> Dict[Any, Any]:
        """Run a Salesforce CLI command asynchronously"""
        try:
            logger.debug(f"Running SF CLI: {' '.join(command)}")
            process = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"SF CLI failed: {error_msg}")
                raise Exception(f"Salesforce CLI command failed: {error_msg}")

            return json.loads(stdout.decode())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse SF CLI JSON output: {e}")
            raise Exception(f"Failed to parse Salesforce CLI output: {e}")
        except FileNotFoundError:
            logger.error("Salesforce CLI (sf) not found")
            raise Exception(
                "Salesforce CLI (sf) not found. Please install the Salesforce CLI."
            )
        except Exception as e:
            logger.error(f"SF CLI command error: {e}")
            raise Exception(f"Error running Salesforce CLI command: {e}")

    async def run_soql(self, soql: str) -> List[Dict[str, Any]]:
        """Run a SOQL query and return the records"""
        command = ["sf", "data", "query", "--query", soql, "--result-format", "json"]
        result = await self._run_cli_command(command)

        if "result" in result and "records" in result["result"]:
            return result["result"]["records"]
        else:
            raise Exception("Unexpected response format from Salesforce CLI")

    async def list_objects(self) -> List[str]:
        """Get list of all Salesforce object names"""
        command = ["sf", "force:schema:sobject:list", "--json"]
        result = await self._run_cli_command(command)

        if "result" in result and isinstance(result["result"], list):
            return result["result"]
        else:
            raise Exception("Unexpected response format from Salesforce CLI")

    async def describe_object(self, object_name: str) -> Dict[str, Any]:
        """Get detailed information about a Salesforce object"""
        command = ["sf", "force:schema:sobject:describe", "-s", object_name, "--json"]
        result = await self._run_cli_command(command)

        if "result" in result:
            return result["result"]
        else:
            raise Exception("Unexpected response format from Salesforce CLI")
