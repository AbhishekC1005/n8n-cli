"""
Async n8n API Client for ADK Agent
===================================
Self-contained HTTP client that talks directly to the n8n REST API.
No dependency on the parent project's n8n module — this is standalone
so the ADK agent package works independently.

Tested against n8n REST API v1 (n8n >= 1.x).
"""

import os
from typing import Optional, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678").rstrip("/")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")


class N8nAPIError(Exception):
    """Raised when an n8n API call fails."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"n8n API error {status_code}: {message}")


class N8nClient:
    """Lightweight async client for n8n REST API v1."""

    def __init__(
        self,
        base_url: str = N8N_BASE_URL,
        api_key: str = N8N_API_KEY,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"X-N8N-API-KEY": self.api_key},
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _handle(self, resp: httpx.Response) -> dict:
        if resp.status_code == 401:
            raise N8nAPIError(401, "Invalid API key")
        if resp.status_code == 404:
            raise N8nAPIError(404, "Resource not found")
        if resp.status_code >= 400:
            raise N8nAPIError(resp.status_code, resp.text[:500])
        return resp.json()

    # ── Health ───────────────────────────────────────────────────────────
    async def ping(self) -> bool:
        try:
            c = await self._get_client()
            resp = await c.get("/api/v1/workflows", params={"limit": 1})
            return resp.status_code == 200
        except Exception:
            return False

    # ── Workflows ────────────────────────────────────────────────────────
    async def get_workflows(self) -> list[dict]:
        c = await self._get_client()
        resp = await c.get("/api/v1/workflows")
        data = self._handle(resp)
        return data.get("data", [])

    async def get_workflow(self, workflow_id: str) -> dict:
        c = await self._get_client()
        resp = await c.get(f"/api/v1/workflows/{workflow_id}")
        data = self._handle(resp)
        return data.get("data", data)

    async def create_workflow(self, workflow_data: dict) -> dict:
        """Create a workflow. Only sends fields the n8n API accepts."""
        # n8n API only accepts specific top-level fields
        clean_data = {
            "name": workflow_data.get("name", "Untitled Workflow"),
        }
        if "nodes" in workflow_data:
            clean_data["nodes"] = workflow_data["nodes"]
        if "connections" in workflow_data:
            clean_data["connections"] = workflow_data["connections"]
        if "settings" in workflow_data:
            clean_data["settings"] = workflow_data["settings"]
        if "staticData" in workflow_data:
            clean_data["staticData"] = workflow_data["staticData"]

        c = await self._get_client()
        resp = await c.post("/api/v1/workflows", json=clean_data)
        data = self._handle(resp)
        return data.get("data", data)

    async def update_workflow(self, workflow_id: str, workflow_data: dict) -> dict:
        """Update a workflow. Only sends fields the n8n API accepts via PUT."""
        clean_data = {}
        if "name" in workflow_data:
            clean_data["name"] = workflow_data["name"]
        if "nodes" in workflow_data:
            clean_data["nodes"] = workflow_data["nodes"]
        if "connections" in workflow_data:
            clean_data["connections"] = workflow_data["connections"]
        if "settings" in workflow_data:
            clean_data["settings"] = workflow_data["settings"]
        if "staticData" in workflow_data:
            clean_data["staticData"] = workflow_data["staticData"]

        c = await self._get_client()
        resp = await c.put(f"/api/v1/workflows/{workflow_id}", json=clean_data)
        data = self._handle(resp)
        return data.get("data", data)

    async def activate_workflow(self, workflow_id: str) -> dict:
        """Activate a workflow via POST /workflows/{id}/activate."""
        c = await self._get_client()
        resp = await c.post(f"/api/v1/workflows/{workflow_id}/activate")
        data = self._handle(resp)
        return data.get("data", data)

    async def deactivate_workflow(self, workflow_id: str) -> dict:
        """Deactivate a workflow via POST /workflows/{id}/deactivate."""
        c = await self._get_client()
        resp = await c.post(f"/api/v1/workflows/{workflow_id}/deactivate")
        data = self._handle(resp)
        return data.get("data", data)

    async def delete_workflow(self, workflow_id: str) -> dict:
        c = await self._get_client()
        resp = await c.delete(f"/api/v1/workflows/{workflow_id}")
        return self._handle(resp)

    # ── Executions ───────────────────────────────────────────────────────
    async def get_executions(self, workflow_id: Optional[str] = None, limit: int = 10) -> list[dict]:
        c = await self._get_client()
        params: dict[str, Any] = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        resp = await c.get("/api/v1/executions", params=params)
        data = self._handle(resp)
        return data.get("data", [])

    # ── Credentials ──────────────────────────────────────────────────────
    async def get_credentials(self) -> list[dict]:
        c = await self._get_client()
        resp = await c.get("/api/v1/credentials")
        data = self._handle(resp)
        return data.get("data", [])


# Module-level singleton
n8n = N8nClient()
