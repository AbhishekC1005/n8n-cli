import typer
from rich.table import Table
from rich.console import Console

from n8n.client import client
from packages.cli.display import show_table, show_spinner, show_error

console = Console()


async def list_workflows_cmd():
    with show_spinner("Fetching workflows..."):
        try:
            workflows = await client.get_workflows()
        except Exception as e:
            show_error(f"Failed to fetch workflows: {e}")
            return
    if not workflows:
        console.print("[dim]No workflows found.[/dim]")
        return
    show_table(workflows)
