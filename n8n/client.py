from typing import Optional
import httpx
from pydantic import ValidationError

from n8n.schemas import (
    WorkflowSummary,
    WorkflowDetail,
    WorkflowData,
    CredentialSummary,
    NodeInfo,
)
from config import settings


class N8nClientError(Exception):
    pass


class N8nConnectionError(N8nClientError):
    pass


class N8nAuthError(N8nClientError):
    pass


class N8nNotFoundError(N8nClientError):
    pass


class N8nClient:
    def __init__(self):
        self.base_url = settings.N8N_BASE_URL.rstrip("/")
        self.api_key = settings.N8N_API_KEY
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"X-N8N-API-KEY": self.api_key},
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _handle_response(self, response: httpx.Response):
        if response.status_code == 401:
            raise N8nAuthError("Invalid API key")
        if response.status_code == 404:
            raise N8nNotFoundError("Resource not found")
        if response.status_code >= 400:
            raise N8nClientError(f"HTTP {response.status_code}: {response.text}")
        return response

    async def ping(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get("/api/v1/workflows", params={"limit": 1})
            self._handle_response(response)
            return response.status_code == 200
        except (httpx.RequestError, N8nClientError):
            return False

    async def get_workflows(self) -> list[WorkflowSummary]:
        client = await self._get_client()
        response = await client.get("/api/v1/workflows")
        self._handle_response(response)
        data = response.json()
        return [WorkflowSummary(**item) for item in data.get("data", [])]

    async def get_workflow(self, workflow_id: str) -> WorkflowDetail:
        client = await self._get_client()
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        self._handle_response(response)
        data = response.json()
        if "data" in data:
            data = data["data"]
        return WorkflowDetail.model_validate(data)

    async def create_workflow(self, data: WorkflowData) -> WorkflowDetail:
        client = await self._get_client()
        response = await client.post("/api/v1/workflows", json=data.model_dump())
        self._handle_response(response)
        result_data = response.json()
        if "data" in result_data:
            result_data = result_data["data"]
        return WorkflowDetail.model_validate(result_data)

    async def update_workflow(
        self, workflow_id: str, data: WorkflowData
    ) -> WorkflowDetail:
        client = await self._get_client()
        response = await client.put(
            f"/api/v1/workflows/{workflow_id}", json=data.model_dump()
        )
        self._handle_response(response)
        result_data = response.json()
        if "data" in result_data:
            result_data = result_data["data"]
        return WorkflowDetail.model_validate(result_data)

    async def activate_workflow(self, workflow_id: str, active: bool) -> WorkflowDetail:
        client = await self._get_client()
        response = await client.patch(
            f"/api/v1/workflows/{workflow_id}", json={"active": active}
        )
        self._handle_response(response)
        result_data = response.json()
        if "data" in result_data:
            result_data = result_data["data"]
        return WorkflowDetail.model_validate(result_data)

    async def delete_workflow(self, workflow_id: str) -> None:
        client = await self._get_client()
        response = await client.delete(f"/api/v1/workflows/{workflow_id}")
        self._handle_response(response)

    async def get_credentials(self) -> list[CredentialSummary]:
        client = await self._get_client()
        response = await client.get("/api/v1/credentials")
        self._handle_response(response)
        data = response.json()
        return [CredentialSummary(**item) for item in data.get("data", [])]

    async def get_installed_nodes(self) -> list[NodeInfo]:
        client = await self._get_client()
        response = await client.get("/api/v1/nodes")
        self._handle_response(response)
        data = response.json()
        return [NodeInfo(**item) for item in data.get("data", [])]


client = N8nClient()
