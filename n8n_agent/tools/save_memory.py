"""
save_memory tool for writing preferences to the memory store.
"""

from n8n_agent.tools.memory_store import memory_store


async def save_memory(key: str, value: str) -> dict:
    """
    Save a user preference or note to memory for later recall.

    Args:
        key: A short key describing the preference (e.g., 'preferred_trigger').
        value: The value to store.

    Returns:
        Confirmation of the saved preference.
    """
    memory_store[key] = value
    return {
        "status": "success",
        "message": f"Saved preference: {key} = {value}",
    }
