import json
from rich.console import Console

from config import settings
from n8n.client import client
from n8n.schemas import WorkflowData
from storage.backup import restore_workflow, get_latest_backup
from packages.cli.display import show_spinner, show_success, show_error

console = Console()


async def restore_workflow_cmd(workflow_id: str):
    with show_spinner("Looking for backup..."):
        backup_data = await restore_workflow(workflow_id)

    if not backup_data:
        show_error(f"No backup found for workflow {workflow_id}")
        return

    with show_spinner("Restoring workflow..."):
        try:
            wf_data = WorkflowData(**backup_data)
            result = await client.update_workflow(workflow_id, wf_data)
            show_success(
                f"Restored workflow '{result.name}'",
                f"{settings.N8N_BASE_URL}/workflow/{workflow_id}",
            )
        except Exception as e:
            show_error(f"Failed to restore: {e}")
