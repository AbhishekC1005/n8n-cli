"""
get_memory tool for reading stored preferences from memory.
"""

from n8n_agent.tools.memory_store import memory_store


async def get_memory() -> dict:
    """
    Retrieve all stored user preferences and notes from memory.

    Returns:
        A dictionary with all stored preferences.
    """
    if not memory_store:
        return {"status": "success", "message": "No stored preferences.", "preferences": {}}
    return {
        "status": "success",
        "preferences": dict(memory_store),
    }
