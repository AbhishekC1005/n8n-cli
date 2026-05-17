import json
import re
from typing import Optional, Any
import httpx
from rapidfuzz import fuzz

from n8n.client import client
from n8n.schemas import WorkflowData, WorkflowDetail
from storage import memory as memory_storage
from storage.cache import get_cached_nodes, save_nodes_cache
from storage.backup import backup_workflow
from core.validator import validate_workflow
from n8n.node_parser import parse_node_schema


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_installed_nodes",
            "description": "Get list of all installed node types in n8n with their descriptions",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_credentials",
            "description": "Get list of all saved credentials with IDs and types",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_workflows",
            "description": "Get list of all workflows with their IDs, names, and active status",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_workflow",
            "description": "Get full workflow details by ID or fuzzy name match",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_or_name": {
                        "type": "string",
                        "description": "Workflow ID or fuzzy name match",
                    },
                },
                "required": ["id_or_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_node_schema",
            "description": "Get detailed parameter schema for a specific node type",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_type": {
                        "type": "string",
                        "description": "The node type name (e.g., n8n-nodes-http.Request)",
                    },
                },
                "required": ["node_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for API documentation, node usage examples, or troubleshooting",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory",
            "description": "Read stored user preferences from memory",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_workflow",
            "description": "Create a new workflow in n8n",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_json": {
                        "type": "string",
                        "description": "Complete workflow JSON string",
                    },
                },
                "required": ["workflow_json"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_workflow",
            "description": "Update an existing workflow in n8n (requires confirmation)",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "The workflow ID to update",
                    },
                    "workflow_json": {
                        "type": "string",
                        "description": "Complete updated workflow JSON string",
                    },
                },
                "required": ["workflow_id", "workflow_json"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "activate_workflow",
            "description": "Activate or deactivate a workflow",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "The workflow ID"},
                    "active": {
                        "type": "boolean",
                        "description": "True to activate, false to deactivate",
                    },
                },
                "required": ["workflow_id", "active"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_workflow",
            "description": "Delete a workflow from n8n (requires confirmation)",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "The workflow ID to delete",
                    },
                    "workflow_name": {
                        "type": "string",
                        "description": "The workflow name for confirmation",
                    },
                },
                "required": ["workflow_id", "workflow_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Save a user preference to memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Preference key"},
                    "value": {"type": "string", "description": "Preference value"},
                },
                "required": ["key", "value"],
            },
        },
    },
]


WRITE_TOOLS = {
    "create_workflow",
    "update_workflow",
    "activate_workflow",
    "delete_workflow",
}


async def get_installed_nodes() -> str:
    nodes = await get_cached_nodes()
    if not nodes:
        nodes = await client.get_installed_nodes()
        await save_nodes_cache(nodes)
    lines = [f"# Installed Nodes ({len(nodes)} total)"]
    for node in nodes[:50]:
        lines.append(f"## {node.name}")
        lines.append(f"Display: {node.displayName}")
        if node.description:
            lines.append(f"Description: {node.description[:200]}")
        lines.append("")
    return "\n".join(lines)


async def get_credentials() -> str:
    creds = await client.get_credentials()
    if not creds:
        return "No credentials configured"
    lines = ["# Available Credentials"]
    for cred in creds:
        lines.append(f"- {cred.id}: {cred.name} ({cred.type})")
    return "\n".join(lines)


async def list_workflows() -> str:
    workflows = await client.get_workflows()
    if not workflows:
        return "No workflows found"
    lines = ["# Workflows"]
    for wf in workflows:
        status = "ACTIVE" if wf.active else "inactive"
        lines.append(f"- {wf.id}: {wf.name} [{status}]")
    return "\n".join(lines)


async def get_workflow(id_or_name: str) -> str:
    try:
        wf = await client.get_workflow(id_or_name)
        return json.dumps(wf.model_dump(), indent=2)
    except Exception:
        workflows = await client.get_workflows()
        matches = []
        for wf in workflows:
            score = fuzz.ratio(id_or_name.lower(), wf.name.lower())
            if score > 60:
                matches.append((score, wf))
        if matches:
            matches.sort(reverse=True)
            best = matches[0][1]
            wf = await client.get_workflow(best.id)
            return json.dumps(wf.model_dump(), indent=2)
        return f"Workflow not found: {id_or_name}"


async def get_node_schema(node_type: str) -> str:
    nodes = await get_cached_nodes()
    if not nodes:
        nodes = await client.get_installed_nodes()
    for node in nodes:
        if node.name == node_type:
            return json.dumps(parse_node_schema(node), indent=2)
    return f"Node type not found: {node_type}"


async def web_search(query: str) -> str:
    encoded_query = (
        httpx.URL(query).str if hasattr(httpx.URL, "str") else query.replace(" ", "+")
    )
    search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
    try:
        async with httpx.AsyncClient() as http:
            resp = await http.get(search_url, timeout=10.0)
            if resp.status_code == 200:
                return f"Search results for '{query}': {search_url}"
            return f"Search failed: {resp.status_code}"
    except Exception as e:
        return f"Search error: {str(e)}"


async def get_memory() -> str:
    return memory_storage.format_for_prompt()


async def create_workflow(workflow_json: str) -> str:
    try:
        wf_data = json.loads(workflow_json)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    error = await validate_workflow(wf_data)
    if error:
        return f"Validation failed: {error}"

    wf = await client.create_workflow(WorkflowData(**wf_data))
    return f"Created workflow '{wf.name}' with ID {wf.id}"


async def update_workflow(workflow_id: str, workflow_json: str) -> str:
    try:
        current = await client.get_workflow(workflow_id)
    except Exception as e:
        return f"Failed to get workflow: {e}"

    await backup_workflow(current)

    try:
        wf_data = json.loads(workflow_json)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    error = await validate_workflow(wf_data)
    if error:
        return f"Validation failed: {error}"

    wf = await client.update_workflow(workflow_id, WorkflowData(**wf_data))
    return f"Updated workflow '{wf.name}' (ID: {wf.id})"


async def activate_workflow(workflow_id: str, active: bool) -> str:
    wf = await client.activate_workflow(workflow_id, active)
    status = "activated" if active else "deactivated"
    return f"Workflow '{wf.name}' {status}"


async def delete_workflow(workflow_id: str, workflow_name: str) -> str:
    await client.delete_workflow(workflow_id)
    return f"Deleted workflow '{workflow_name}' (ID: {workflow_id})"


async def save_memory_key_value(key: str, value: str) -> str:
    memory_storage.save_memory(key, value)
    return f"Saved preference: {key} = {value}"


async def execute_tool(name: str, args: dict) -> str:
    tool_map = {
        "get_installed_nodes": get_installed_nodes,
        "get_credentials": get_credentials,
        "list_workflows": list_workflows,
        "get_workflow": get_workflow,
        "get_node_schema": get_node_schema,
        "web_search": web_search,
        "get_memory": get_memory,
        "create_workflow": create_workflow,
        "update_workflow": update_workflow,
        "activate_workflow": activate_workflow,
        "delete_workflow": delete_workflow,
        "save_memory": save_memory_key_value,
    }

    if name not in tool_map:
        return f"Unknown tool: {name}"

    try:
        result = await tool_map[name](**args)
        return result
    except Exception as e:
        return f"Tool error: {str(e)}"
