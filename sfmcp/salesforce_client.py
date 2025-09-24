from __future__ import annotations
import json
import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List
from .config.settings import settings

logger = logging.getLogger("sfmcp.client")


class SalesforceClient:
    def __init__(self, *, instance_url: str, access_token: str, org_alias: str):
        self._instance_url = instance_url
        self._access_token = access_token
        self._org_alias = org_alias

    @classmethod
    def from_env(cls) -> "SalesforceClient":
        return cls(
            instance_url=settings.sf_instance_url,
            access_token=settings.sf_access_token,
            org_alias=settings.sf_org_alias,
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

            result = json.loads(stdout.decode())
            return result  # type: ignore[no-any-return]

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
        command = [
            "sf",
            "data",
            "query",
            "--target-org",
            self._org_alias,
            "--query",
            soql,
            "--result-format",
            "json",
        ]
        result = await self._run_cli_command(command)

        if "result" in result and "records" in result["result"]:
            return result["result"]["records"]  # type: ignore[no-any-return]
        else:
            raise Exception("Unexpected response format from Salesforce CLI")

    async def list_objects(self) -> List[str]:
        """Get list of all Salesforce object names"""
        command = [
            "sf",
            "force:schema:sobject:list",
            "--target-org",
            self._org_alias,
            "--json",
        ]
        result = await self._run_cli_command(command)

        if "result" in result and isinstance(result["result"], list):
            return result["result"]
        else:
            raise Exception("Unexpected response format from Salesforce CLI")

    async def describe_object(self, object_name: str) -> Dict[str, Any]:
        """Get detailed information about a Salesforce object"""
        command = [
            "sf",
            "force:schema:sobject:describe",
            "--target-org",
            self._org_alias,
            "-s",
            object_name,
            "--json",
        ]
        result = await self._run_cli_command(command)

        if "result" in result:
            return result["result"]  # type: ignore[no-any-return]
        else:
            raise Exception("Unexpected response format from Salesforce CLI")

    async def list_flows(self) -> List[Dict[str, Any]]:
        """Get list of Salesforce flows using tooling API, joined with FlowDefinition"""
        # Query 1: Get Flow records (all versions)
        flow_command = [
            "sf",
            "data",
            "query",
            "--target-org",
            self._org_alias,
            "--use-tooling-api",
            "-q",
            "SELECT Id, MasterLabel, Status, VersionNumber FROM Flow",
            "--json",
        ]
        flow_result = await self._run_cli_command(flow_command)

        # Query 2: Get FlowDefinition records
        flow_def_command = [
            "sf",
            "data",
            "query",
            "--target-org",
            self._org_alias,
            "--use-tooling-api",
            "-q",
            "SELECT Id, DeveloperName, ActiveVersionId, LatestVersionId FROM FlowDefinition",
            "--json",
        ]
        flow_def_result = await self._run_cli_command(flow_def_command)

        # Extract results
        if (
            "result" not in flow_result
            or "records" not in flow_result["result"]
            or "result" not in flow_def_result
            or "records" not in flow_def_result["result"]
        ):
            raise Exception("Unexpected response format from Salesforce CLI")

        flows_data = flow_result["result"]["records"]
        flow_defs_data = flow_def_result["result"]["records"]

        # Create a mapping of Flow ID to Flow data
        flows_by_id = {flow["Id"]: flow for flow in flows_data}

        # Join the data and get only latest versions
        combined_flows = []
        for flow_def in flow_defs_data:
            latest_version_id = flow_def.get("LatestVersionId")
            active_version_id = flow_def.get("ActiveVersionId")

            # Use the latest version ID to get the flow details
            if latest_version_id and latest_version_id in flows_by_id:
                flow = flows_by_id[latest_version_id]

                combined_flow = {
                    "id": flow["Id"],
                    "masterLabel": flow["MasterLabel"],
                    "status": flow["Status"],
                    "versionNumber": flow["VersionNumber"],
                    "developerName": flow_def["DeveloperName"],
                    "definitionId": flow_def["Id"],
                    "isActive": latest_version_id == active_version_id,
                    "activeVersionId": active_version_id,
                    "latestVersionId": latest_version_id,
                }
                combined_flows.append(combined_flow)

        # Sort by MasterLabel
        combined_flows.sort(key=lambda x: x["masterLabel"] or "")

        return combined_flows

    async def list_reports(self) -> List[Dict[str, Any]]:
        """Get list of Salesforce reports"""
        command = [
            "sf",
            "data",
            "query",
            "--target-org",
            self._org_alias,
            "--query",
            "SELECT Id, Name, DeveloperName, Format, FolderName, Description, OwnerId, LastRunDate, LastViewedDate, LastReferencedDate FROM Report ORDER BY FolderName, Name",
            "--result-format",
            "json",
        ]

        result = await self._run_cli_command(command)

        if "result" in result and "records" in result["result"]:
            reports_data = result["result"]["records"]

            # Process reports to add calculated fields
            processed_reports = []
            for report in reports_data:
                processed_report = {
                    "id": report.get("Id"),
                    "name": report.get("Name"),
                    "developerName": report.get("DeveloperName"),
                    "format": report.get("Format"),
                    "folderName": report.get("FolderName", "Unfiled Public Reports"),
                    "description": report.get("Description"),
                    "ownerId": report.get("OwnerId"),
                    "lastRunDate": report.get("LastRunDate"),
                    "lastViewedDate": report.get("LastViewedDate"),
                    "lastReferencedDate": report.get("LastReferencedDate"),
                }
                processed_reports.append(processed_report)

            return processed_reports
        else:
            raise Exception("Unexpected response format from Salesforce CLI")

    async def list_dashboards(self) -> List[Dict[str, Any]]:
        """Get list of Salesforce dashboards"""
        command = [
            "sf",
            "data",
            "query",
            "--target-org",
            self._org_alias,
            "--query",
            "SELECT Id, Title, DeveloperName, FolderName, Description, OwnerId, LastViewedDate, LastReferencedDate FROM Dashboard ORDER BY FolderName, Title",
            "--result-format",
            "json",
        ]

        result = await self._run_cli_command(command)

        if "result" in result and "records" in result["result"]:
            dashboards_data = result["result"]["records"]

            # Process dashboards to add calculated fields
            processed_dashboards = []
            for dashboard in dashboards_data:
                processed_dashboard = {
                    "id": dashboard.get("Id"),
                    "title": dashboard.get("Title"),
                    "developerName": dashboard.get("DeveloperName"),
                    "folderName": dashboard.get(
                        "FolderName", "Unfiled Public Dashboards"
                    ),
                    "description": dashboard.get("Description"),
                    "ownerId": dashboard.get("OwnerId"),
                    "lastViewedDate": dashboard.get("LastViewedDate"),
                    "lastReferencedDate": dashboard.get("LastReferencedDate"),
                }
                processed_dashboards.append(processed_dashboard)

            return processed_dashboards
        else:
            raise Exception("Unexpected response format from Salesforce CLI")

    async def describe_flow(self, flow_developer_name: str) -> Dict[str, Any]:
        """Retrieve and read a flow's metadata XML file, then clean up"""
        # Use sf project retrieve to get the flow metadata
        command = [
            "sf", "project", "retrieve", "start",
            "--target-org", self._org_alias,
            "--metadata", f"Flow:{flow_developer_name}",
        ]

        try:
            logger.debug(f"Retrieving flow metadata for: {flow_developer_name}")
            # The retrieve command doesn't return JSON, so we use a different approach
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"SF CLI retrieve failed: {error_msg}")
                raise Exception(f"Salesforce CLI retrieve failed: {error_msg}")

            # Log the retrieve output for debugging
            retrieve_output = stdout.decode()
            logger.debug(f"Retrieve output: {retrieve_output}")

            # The retrieve command doesn't return JSON by default, so we need to find the file
            # Look for the flow file in the standard locations
            possible_paths = [
                f"force-app/main/default/flows/{flow_developer_name}.flow-meta.xml",
                f"src/flows/{flow_developer_name}.flow-meta.xml",
                # Some orgs might use different directory structures
                f"flows/{flow_developer_name}.flow-meta.xml",
                f"metadata/flows/{flow_developer_name}.flow-meta.xml",
            ]

            flow_content = None
            flow_file_path = None

            for path_str in possible_paths:
                path = Path(path_str)
                if path.exists():
                    logger.debug(f"Found flow file at: {path}")
                    flow_file_path = path
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            flow_content = f.read()
                        break
                    except Exception as read_error:
                        logger.error(f"Failed to read flow file {path}: {read_error}")
                        continue

            if flow_content is None:
                # Try to search more broadly in case the file is in a different location
                logger.debug("Flow file not found in standard locations, searching broadly...")
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if file == f"{flow_developer_name}.flow-meta.xml":
                            found_path = Path(root) / file
                            logger.debug(f"Found flow file at: {found_path}")
                            flow_file_path = found_path
                            try:
                                with open(found_path, 'r', encoding='utf-8') as f:
                                    flow_content = f.read()
                                break
                            except Exception as read_error:
                                logger.error(f"Failed to read flow file {found_path}: {read_error}")
                                continue
                    if flow_content:
                        break

            if flow_content is None:
                # Provide more helpful error message with debugging info
                error_msg = f"Flow file not found after retrieve: {flow_developer_name}\n"
                error_msg += f"Retrieve command output: {retrieve_output}\n"
                error_msg += f"Searched paths: {possible_paths}\n"

                # List current directory contents for debugging
                try:
                    current_files = []
                    for root, dirs, files in os.walk("."):
                        for file in files:
                            if flow_developer_name.lower() in file.lower():
                                current_files.append(os.path.join(root, file))
                    if current_files:
                        error_msg += f"Files found with flow name: {current_files}"
                    else:
                        error_msg += "No files found containing the flow name"
                except Exception as search_err:
                    error_msg += f"Error searching for files: {search_err}"

                raise Exception(error_msg)

            # Clean up: remove the retrieved file
            if flow_file_path:
                try:
                    flow_file_path.unlink()
                    logger.debug(f"Cleaned up flow file: {flow_file_path}")

                    # Also clean up empty directories if they exist
                    parent_dir = flow_file_path.parent
                    if parent_dir.exists() and not any(parent_dir.iterdir()):
                        parent_dir.rmdir()
                        logger.debug(f"Cleaned up empty directory: {parent_dir}")

                        # Clean up parent directories if they're empty too
                        grandparent = parent_dir.parent
                        if grandparent.name in ["flows", "default", "main"] and grandparent.exists():
                            if not any(grandparent.iterdir()):
                                grandparent.rmdir()
                                logger.debug(f"Cleaned up empty directory: {grandparent}")

                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up flow file {flow_file_path}: {cleanup_error}")

            return {
                "flowDeveloperName": flow_developer_name,
                "flowContent": flow_content,
                "contentLength": len(flow_content),
                "filePath": str(flow_file_path) if flow_file_path else "unknown",
            }

        except Exception as e:
            logger.error(f"Failed to describe flow {flow_developer_name}: {e}")
            raise Exception(f"Failed to retrieve flow metadata: {e}")
