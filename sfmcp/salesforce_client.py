from __future__ import annotations
from typing import Any, Dict, List
from .config.settings import settings

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

    # Plug this into your existing implementation
    def run_soql(self, soql: str) -> List[Dict[str, Any]]:
        # Example shim: import your real module and delegate
        # from ._internal_sf import run_soql
        # return run_soql(self._instance_url, self._access_token, soql)
        raise NotImplementedError("Wire this to your existing Salesforce query module.")

    # Optional: add describe/report methods as your module supports
    # def describe(self, object_api_name: str) -> Dict[str, Any]: ...
