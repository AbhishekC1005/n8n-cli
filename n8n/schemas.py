from pydantic import BaseModel, Field
from typing import Optional, Any


class NodePosition(BaseModel):
    x: int
    y: int


class NodeParameters(BaseModel):
    pass


class WorkflowNode(BaseModel):
    id: str
    name: str
    type: str
    typeVersion: float
    position: NodePosition
    parameters: dict = Field(default_factory=dict)
    credentials: Optional[dict] = None


class WorkflowConnections(BaseModel):
    pass


class WorkflowSettings(BaseModel):
    executionOrder: str = "v1"


class WorkflowData(BaseModel):
    name: str
    nodes: list[WorkflowNode]
    connections: dict = Field(default_factory=dict)
    settings: WorkflowSettings = Field(default_factory=WorkflowSettings)
    active: bool = False


class WorkflowDetail(BaseModel):
    id: str
    name: str
    nodes: list[WorkflowNode]
    connections: dict = Field(default_factory=dict)
    settings: WorkflowSettings = Field(default_factory=WorkflowSettings)
    active: bool = False
    createdAt: str
    updatedAt: str


class WorkflowSummary(BaseModel):
    id: str
    name: str
    active: bool
    createdAt: str
    updatedAt: str
    nodeCount: int = 0


class CredentialSummary(BaseModel):
    id: str
    name: str
    type: str


class NodeInfo(BaseModel):
    name: str
    displayName: str
    description: str
    version: str
    credentials: Optional[list[str]] = None
