import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any
import uuid

from config import ensure_agent_home, settings

SESSIONS_DIR = ensure_agent_home() / "sessions"
CURRENT_FILE = SESSIONS_DIR / "current.jsonl"
ARCHIVE_DIR = SESSIONS_DIR / "archive"
SESSION_ID = str(uuid.uuid4())[:8]


def get_session_id() -> str:
    return SESSION_ID


def load_session() -> list[dict]:
    if not CURRENT_FILE.exists():
        return []
    messages = []
    try:
        with open(CURRENT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue
    except IOError:
        return []
    return messages


def save_turn(
    role: str,
    content: str,
    tool_calls: Optional[list] = None,
    tool_results: Optional[list] = None,
):
    entry: dict[str, Any] = {}
    entry["role"] = role
    entry["content"] = content
    entry["timestamp"] = datetime.now().isoformat()
    if tool_calls:
        entry["tool_calls"] = tool_calls
    if tool_results:
        entry["tool_results"] = tool_results
    with open(CURRENT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def clear_session():
    if CURRENT_FILE.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = ARCHIVE_DIR / f"{timestamp}.jsonl"
        CURRENT_FILE.rename(archive_file)


def archive_old_sessions():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    if not CURRENT_FILE.exists():
        return
    try:
        with open(CURRENT_FILE, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if not first_line:
                return
            first_msg = json.loads(first_line)
            first_ts = datetime.fromisoformat(
                first_msg.get("timestamp", datetime.now().isoformat())
            )
            if datetime.now() - first_ts > timedelta(days=7):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_file = ARCHIVE_DIR / f"{timestamp}.jsonl"
                CURRENT_FILE.rename(archive_file)
    except (json.JSONDecodeError, IOError, ValueError):
        pass


def get_history() -> list[dict]:
    return load_session()
