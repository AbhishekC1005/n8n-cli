import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from config import settings, ensure_agent_home
from n8n.schemas import NodeInfo


CACHE_DIR = ensure_agent_home() / "cache"
NODES_CACHE_FILE = CACHE_DIR / "nodes.json"


async def get_cached_nodes() -> Optional[list[NodeInfo]]:
    if not NODES_CACHE_FILE.exists():
        return None
    try:
        with open(NODES_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
        if datetime.now() - cached_at > timedelta(seconds=settings.CACHE_TTL):
            return None
        return [NodeInfo(**item) for item in data.get("nodes", [])]
    except (json.JSONDecodeError, IOError, KeyError):
        return None


async def save_nodes_cache(nodes: list[NodeInfo]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "cached_at": datetime.now().isoformat(),
        "nodes": [node.model_dump() for node in nodes],
    }
    with open(NODES_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def is_cache_valid() -> bool:
    if not NODES_CACHE_FILE.exists():
        return False
    try:
        with open(NODES_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
        return datetime.now() - cached_at <= timedelta(seconds=settings.CACHE_TTL)
    except:
        return False
