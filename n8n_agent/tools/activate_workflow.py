"""
activate_workflow tool for toggling workflow active states.
"""

from n8n_agent.client import n8n, N8nAPIError


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
