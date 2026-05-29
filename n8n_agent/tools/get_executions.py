"""
get_executions tool for viewing workflow execution histories.
"""

from n8n_agent.client import n8n


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
