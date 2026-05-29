"""
get_credentials tool for listing active credentials in n8n.
"""

from n8n_agent.client import n8n, N8nAPIError


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
