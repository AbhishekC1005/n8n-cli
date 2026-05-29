"""
create_workflow tool for creating new workflows in n8n.
"""

import json
from n8n_agent.client import n8n, N8nAPIError
from n8n_agent.tools.helpers import validate_workflow_structure


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
        return {"status": "validation_error", "error": f"Invalid JSON: {e}"}

    # Basic structural validation
    validation_error = validate_workflow_structure(wf_data)
    if validation_error:
        return {"status": "validation_error", "error": validation_error}

    try:
        result = await n8n.create_workflow(wf_data)
        return {
            "status": "success",
            "message": f"Created workflow '{result.get('name', '')}' successfully",
            "workflow_id": result.get("id", ""),
            "workflow_name": result.get("name", ""),
        }
    except N8nAPIError as e:
        return {
            "status": "system_error",
            "error": str(e),
            "instructions": "FATAL: Connection or Authentication Error. Do NOT retry. Report this error immediately."
        }
    except Exception as e:
        return {
            "status": "system_error",
            "error": f"Failed to connect to n8n: {e}",
            "instructions": "FATAL: Connection or Authentication Error. Do NOT retry. Report this error immediately."
        }
