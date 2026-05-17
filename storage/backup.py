import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import ensure_agent_home
from n8n.schemas import WorkflowDetail


BACKUPS_DIR = ensure_agent_home() / "backups"


def get_backup_dir(workflow_id: str) -> Path:
    return BACKUPS_DIR / workflow_id


async def backup_workflow(workflow: WorkflowDetail) -> Path:
    workflow_dir = get_backup_dir(workflow.id)
    workflow_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = workflow_dir / f"{timestamp}.json"
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(workflow.model_dump(), f, indent=2)
    await _cleanup_old_backups(workflow.id)
    return backup_file


async def _cleanup_old_backups(workflow_id: str) -> None:
    workflow_dir = get_backup_dir(workflow_id)
    if not workflow_dir.exists():
        return
    backups = sorted(
        workflow_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for old_backup in backups[10:]:
        old_backup.unlink()


async def get_latest_backup(workflow_id: str) -> Optional[Path]:
    workflow_dir = get_backup_dir(workflow_id)
    if not workflow_dir.exists():
        return None
    backups = sorted(
        workflow_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    return backups[0] if backups else None


async def restore_workflow(workflow_id: str) -> Optional[dict]:
    latest = await get_latest_backup(workflow_id)
    if not latest:
        return None
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)
