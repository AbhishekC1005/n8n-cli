import json
from pathlib import Path
from typing import Optional

from config import ensure_agent_home


MEMORY_FILE = ensure_agent_home() / "memory.json"


def get_memory() -> dict:
    if not MEMORY_FILE.exists():
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_memory(key: str, value: str) -> None:
    memory = get_memory()
    memory[key] = value
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def format_for_prompt() -> str:
    memory = get_memory()
    if not memory:
        return "No stored preferences."
    lines = ["Stored user preferences:"]
    for key, value in memory.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def get_memory_value(key: str) -> Optional[str]:
    memory = get_memory()
    return memory.get(key)
