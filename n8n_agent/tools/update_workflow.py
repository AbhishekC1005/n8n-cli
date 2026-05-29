"""
update_workflow tool for updating existing workflows in n8n.
"""

import json
from n8n_agent.client import n8n, N8nAPIError
from n8n_agent.tools.helpers import validate_workflow_structure


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
        return {"status": "validation_error", "error": f"Invalid JSON: {e}"}

    validation_error = validate_workflow_structure(wf_data)
    if validation_error:
        return {"status": "validation_error", "error": validation_error}

    try:
        result = await n8n.update_workflow(workflow_id, wf_data)
        return {
            "status": "success",
            "message": f"Updated workflow '{result.get('name', '')}' successfully",
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
