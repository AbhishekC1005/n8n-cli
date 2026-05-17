import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from packages.cli.session import load_session, ARCHIVE_DIR
from packages.cli.display import show_error

console = Console()


async def show_history_cmd():
    messages = load_session()
    if not messages:
        console.print("[dim]No session history.[/dim]")
        return

    table = Table(title="Session History")
    table.add_column("#", style="dim")
    table.add_column("Role", style="cyan")
    table.add_column("Content", style="white", max_width=80)
    table.add_column("Time", style="dim")

    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if len(content) > 100:
            content = content[:100] + "..."
        timestamp = msg.get("timestamp", "")[:19]
        table.add_row(str(i), role, content, timestamp)

    console.print(table)

    archive_files = sorted(ARCHIVE_DIR.glob("*.jsonl")) if ARCHIVE_DIR.exists() else []
    if archive_files:
        console.print(f"\n[dim]Archived sessions: {len(archive_files)} files[/dim]")
        for af in archive_files[-5:]:
            console.print(f"  [dim]{af.name}[/dim]")
