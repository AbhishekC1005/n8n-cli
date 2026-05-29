"""
list_workflows tool for listing all workflows in n8n.
"""

from n8n_agent.client import n8n, N8nAPIError


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
