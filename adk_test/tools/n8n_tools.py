"""
n8n Tool Definitions for Google ADK Agent
==========================================
Each function here becomes a callable tool in the ADK agent.
Google ADK automatically wraps plain Python functions (sync or async)
as FunctionTools — docstrings become tool descriptions, and type hints
become the parameter schema.

All tools that interact with n8n are async and use the self-contained
n8n_client module.
"""

import json
from typing import Optional
from rapidfuzz import fuzz

from adk_test.tools.n8n_client import n8n, N8nAPIError


# ═══════════════════════════════════════════════════════════════════════════
#  READ-ONLY TOOLS
# ═══════════════════════════════════════════════════════════════════════════


async def get_credentials() -> dict:
    """
    Get list of all saved credentials in n8n with their IDs, names, and types.
    Call this BEFORE assigning credentials to workflow nodes so you use the correct credential IDs.

    Returns:
        A dictionary with status and a list of available credentials.
    """
    try:
        creds = await n8n.get_credentials()
        cred_list = []
        for cred in creds:
            cred_list.append({
                "id": cred.get("id", ""),
                "name": cred.get("name", ""),
                "type": cred.get("type", ""),
            })
        return {
            "status": "success",
            "count": len(cred_list),
            "credentials": cred_list,
        }
    except N8nAPIError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Failed to fetch credentials: {e}"}


async def list_workflows() -> dict:
    """
    Get list of all workflows in n8n with their IDs, names, and active status.
    Use this to see what workflows already exist before creating new ones.

    Returns:
        A dictionary with status and a list of workflow summaries.
    """
    try:
        workflows = await n8n.get_workflows()
        wf_list = []
        for wf in workflows:
            wf_list.append({
                "id": wf.get("id", ""),
                "name": wf.get("name", ""),
                "active": wf.get("active", False),
                "createdAt": wf.get("createdAt", ""),
                "updatedAt": wf.get("updatedAt", ""),
            })
        return {
            "status": "success",
            "count": len(wf_list),
            "workflows": wf_list,
        }
    except N8nAPIError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Failed to fetch workflows: {e}"}


async def get_workflow(id_or_name: str) -> dict:
    """
    Get full workflow details by ID or by fuzzy name match.
    Returns the complete workflow JSON including nodes, connections, and settings.

    Args:
        id_or_name: The workflow ID (numeric string) or a name to fuzzy-match.

    Returns:
        A dictionary with the full workflow detail or an error message.
    """
    try:
        # Try direct ID lookup first
        wf = await n8n.get_workflow(id_or_name)
        return {"status": "success", "workflow": wf}
    except N8nAPIError:
        pass
    except Exception:
        pass

    # Fuzzy name match fallback
    try:
        workflows = await n8n.get_workflows()
        matches = []
        for wf in workflows:
            score = fuzz.ratio(id_or_name.lower(), wf.get("name", "").lower())
            if score > 60:
                matches.append((score, wf))

        if matches:
            matches.sort(key=lambda x: x[0], reverse=True)
            best_id = matches[0][1].get("id", "")
            wf = await n8n.get_workflow(best_id)
            return {"status": "success", "matched_name": matches[0][1].get("name"), "workflow": wf}

        return {"status": "error", "error": f"Workflow not found: '{id_or_name}'"}
    except Exception as e:
        return {"status": "error", "error": f"Search failed: {e}"}


async def get_executions(workflow_id: str = "", limit: int = 10) -> dict:
    """
    Get recent execution history for a workflow (or all workflows).
    Useful for debugging workflow failures.

    Args:
        workflow_id: Optional workflow ID to filter by. Leave empty for all.
        limit: Maximum number of executions to return (default 10).

    Returns:
        A dictionary with status and a list of execution summaries.
    """
    try:
        wf_id = workflow_id if workflow_id else None
        executions = await n8n.get_executions(workflow_id=wf_id, limit=limit)
        exec_list = []
        for ex in executions:
            exec_list.append({
                "id": ex.get("id", ""),
                "workflowId": ex.get("workflowId", ""),
                "status": ex.get("status", ""),
                "startedAt": ex.get("startedAt", ""),
                "stoppedAt": ex.get("stoppedAt", ""),
            })
        return {"status": "success", "count": len(exec_list), "executions": exec_list}
    except Exception as e:
        return {"status": "error", "error": f"Failed to fetch executions: {e}"}


# ═══════════════════════════════════════════════════════════════════════════
#  WRITE / MUTATING TOOLS
# ═══════════════════════════════════════════════════════════════════════════


async def create_workflow(workflow_json: str) -> dict:
    """
    Create a new workflow in n8n from a JSON string.
    The JSON must follow the n8n workflow format with nodes, connections, and settings.
    ONLY call this when the user explicitly asks to create a workflow.

    Args:
        workflow_json: A complete n8n workflow as a JSON string. Must include
            'name', 'nodes' (array), 'connections' (object), and 'settings'.

    Returns:
        A dictionary with the created workflow's ID and name, or an error.
    """
    try:
        wf_data = json.loads(workflow_json)
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON: {e}"}

    # Basic structural validation
    validation_error = _validate_workflow_structure(wf_data)
    if validation_error:
        return {"status": "error", "error": validation_error}

    try:
        result = await n8n.create_workflow(wf_data)
        return {
            "status": "success",
            "message": f"Created workflow '{result.get('name', '')}' successfully",
            "workflow_id": result.get("id", ""),
            "workflow_name": result.get("name", ""),
        }
    except N8nAPIError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Failed to create workflow: {e}"}


async def update_workflow(workflow_id: str, workflow_json: str) -> dict:
    """
    Update an existing workflow in n8n. Replaces the workflow content entirely.
    ONLY call this when the user explicitly asks to update/edit a workflow.

    Args:
        workflow_id: The ID of the workflow to update.
        workflow_json: The complete updated workflow as a JSON string.

    Returns:
        A dictionary with the updated workflow's ID and name, or an error.
    """
    try:
        wf_data = json.loads(workflow_json)
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON: {e}"}

    validation_error = _validate_workflow_structure(wf_data)
    if validation_error:
        return {"status": "error", "error": validation_error}

    try:
        result = await n8n.update_workflow(workflow_id, wf_data)
        return {
            "status": "success",
            "message": f"Updated workflow '{result.get('name', '')}' successfully",
            "workflow_id": result.get("id", ""),
            "workflow_name": result.get("name", ""),
        }
    except N8nAPIError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Failed to update workflow: {e}"}


async def activate_workflow(workflow_id: str, active: bool) -> dict:
    """
    Activate or deactivate a workflow in n8n.
    ONLY call this when the user explicitly asks to activate or deactivate a workflow.

    Args:
        workflow_id: The ID of the workflow.
        active: True to activate, False to deactivate.

    Returns:
        A dictionary with the workflow status after the change.
    """
    try:
        if active:
            result = await n8n.activate_workflow(workflow_id)
        else:
            result = await n8n.deactivate_workflow(workflow_id)
        status_str = "activated" if active else "deactivated"
        return {
            "status": "success",
            "message": f"Workflow '{result.get('name', '')}' {status_str}",
            "workflow_id": result.get("id", ""),
            "active": result.get("active", active),
        }
    except N8nAPIError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Failed to change workflow status: {e}"}


async def delete_workflow(workflow_id: str, workflow_name: str) -> dict:
    """
    Delete a workflow from n8n. This action is IRREVERSIBLE.
    NEVER call this unless the user has EXPLICITLY asked to delete a specific workflow.

    Args:
        workflow_id: The ID of the workflow to delete.
        workflow_name: The name of the workflow (for confirmation/logging).

    Returns:
        A dictionary confirming the deletion or an error.
    """
    try:
        await n8n.delete_workflow(workflow_id)
        return {
            "status": "success",
            "message": f"Deleted workflow '{workflow_name}' (ID: {workflow_id})",
        }
    except N8nAPIError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Failed to delete workflow: {e}"}


# ═══════════════════════════════════════════════════════════════════════════
#  MEMORY / PREFERENCE TOOLS
# ═══════════════════════════════════════════════════════════════════════════


_memory_store: dict[str, str] = {}


async def save_memory(key: str, value: str) -> dict:
    """
    Save a user preference or note to memory for later recall.

    Args:
        key: A short key describing the preference (e.g., 'preferred_trigger').
        value: The value to store.

    Returns:
        Confirmation of the saved preference.
    """
    _memory_store[key] = value
    return {
        "status": "success",
        "message": f"Saved preference: {key} = {value}",
    }


async def get_memory() -> dict:
    """
    Retrieve all stored user preferences and notes from memory.

    Returns:
        A dictionary with all stored preferences.
    """
    if not _memory_store:
        return {"status": "success", "message": "No stored preferences.", "preferences": {}}
    return {
        "status": "success",
        "preferences": dict(_memory_store),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  WEB SEARCH TOOL
# ═══════════════════════════════════════════════════════════════════════════


async def web_search(query: str) -> dict:
    """
    Search the web for n8n documentation, API usage examples, or troubleshooting.
    Use this when you need information about n8n node parameters, third-party APIs,
    or how to configure specific integrations.

    Args:
        query: The search query string.

    Returns:
        A dictionary with search results or a search URL.
    """
    import httpx as _httpx

    search_query = query.replace(" ", "+")
    search_url = f"https://duckduckgo.com/html/?q={search_query}+n8n"
    try:
        async with _httpx.AsyncClient() as http:
            resp = await http.get(
                search_url,
                timeout=10.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; n8nAgent/1.0)"},
            )
            if resp.status_code == 200:
                return {
                    "status": "success",
                    "query": query,
                    "message": f"Search results available at: {search_url}",
                    "hint": "Based on common n8n documentation patterns, try using the node type and parameters described in the official n8n docs.",
                }
            return {"status": "error", "error": f"Search returned status {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "error": f"Search failed: {e}"}


# ═══════════════════════════════════════════════════════════════════════════
#  INTERNAL HELPERS (not exposed as tools)
# ═══════════════════════════════════════════════════════════════════════════


def _validate_workflow_structure(wf_data: dict) -> Optional[str]:
    """Validate basic n8n workflow structure. Returns error string or None."""
    if not isinstance(wf_data, dict):
        return "Workflow must be a JSON object"

    if "name" not in wf_data:
        return "Workflow must have a 'name' field"

    nodes = wf_data.get("nodes")
    if not isinstance(nodes, list) or len(nodes) == 0:
        return "Workflow must have a non-empty 'nodes' array"

    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            return f"Node at index {i} must be a JSON object"
        for required in ("name", "type", "position"):
            if required not in node:
                return f"Node '{node.get('name', f'index {i}')}' is missing required field '{required}'"
        pos = node.get("position")
        if isinstance(pos, dict) and ("x" not in pos or "y" not in pos):
            return f"Node '{node['name']}' position must have 'x' and 'y' fields"
        elif isinstance(pos, list) and len(pos) < 2:
            return f"Node '{node['name']}' position array must have at least 2 elements [x, y]"

    # Check for trigger node
    has_trigger = any(
        "Trigger" in node.get("type", "") or "Webhook" in node.get("type", "") or "Schedule" in node.get("type", "")
        for node in nodes
    )
    if not has_trigger:
        return "Workflow should have at least one trigger node (type containing 'Trigger', 'Webhook', or 'Schedule')"

    return None
