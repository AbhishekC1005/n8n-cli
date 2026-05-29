"""
get_workflow tool for retrieving full workflow details from n8n.
"""

from rapidfuzz import fuzz
from n8n_agent.client import n8n, N8nAPIError


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
