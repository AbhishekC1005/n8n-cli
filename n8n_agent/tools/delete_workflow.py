"""
delete_workflow tool for permanently destroying workflows in n8n.
"""

from n8n_agent.client import n8n, N8nAPIError


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
