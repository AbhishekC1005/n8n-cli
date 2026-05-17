from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from rich.json import JSON
from typing import Optional, Iterator
import json

console = Console()


class show_spinner:
    def __init__(self, message: str):
        self.message = message
        self.spinner = Spinner("dots", text=message)
        self.live = None

    def __enter__(self):
        self.live = Live(self.spinner, console=console, refresh_per_second=10)
        self.live.start()
        return self

    def __exit__(self, *args):
        if self.live:
            self.live.stop()


def show_workflow_preview(workflow_data: dict):
    nodes = workflow_data.get("nodes", [])
    connections = workflow_data.get("connections", {})
    node_lines = [f"  [cyan]{n.get('name')}[/cyan] -> {n.get('type')}" for n in nodes]
    conn_lines = []
    for src, outputs in connections.items():
        for out_key, conns in outputs.items():
            for conn_list in conns:
                for conn in conn_list:
                    conn_lines.append(f"  {src} -> {conn.get('node')}")
    content = f"[bold]{workflow_data.get('name', 'Unnamed')}[/bold]\n\n"
    content += f"[dim]Nodes ({len(nodes)}):[/dim]\n" + "\n".join(node_lines)
    if conn_lines:
        content += f"\n\n[dim]Connections:[/dim]\n" + "\n".join(conn_lines)
    console.print(Panel(content, title="Workflow Preview", border_style="blue"))


def show_diff(old: dict, new: dict):
    old_json = json.dumps(old, indent=2, sort_keys=True)
    new_json = json.dumps(new, indent=2, sort_keys=True)
    old_lines = old_json.splitlines()
    new_lines = new_json.splitlines()
    diff_lines = []
    max_lines = max(len(old_lines), len(new_lines))
    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""
        if old_line != new_line:
            if old_line and not new_line:
                diff_lines.append(f"[red]- {old_line}[/red]")
            elif new_line and not old_line:
                diff_lines.append(f"[green]+ {new_line}[/green]")
            else:
                diff_lines.append(f"[red]- {old_line}[/red]")
                diff_lines.append(f"[green]+ {new_line}[/green]")
    console.print(
        Panel(
            Text.from_ansi("\n".join(diff_lines[:50])),
            title="Workflow Diff",
            border_style="yellow",
        )
    )


def show_success(message: str, url: Optional[str] = None):
    text = message
    if url:
        text += f"\n[dim]URL: {url}[/dim]"
    console.print(Panel(text, title="Success", border_style="green"))


def show_error(message: str):
    console.print(Panel(message, title="Error", border_style="red"))


def show_table(workflows: list):
    table = Table(title="Workflows")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")
    table.add_column("Nodes", style="dim")
    table.add_column("Modified", style="dim")
    for wf in workflows:
        status = "[green]ACTIVE[/green]" if wf.active else "[dim]inactive[/dim]"
        table.add_row(
            str(wf.id),
            wf.name,
            status,
            str(wf.nodeCount),
            wf.updatedAt[:10],
        )
    console.print(table)


def show_tool_call(tool_name: str, args: dict):
    args_str = json.dumps(args, default=str)[:100]
    console.print(f"[dim]  Calling tool: {tool_name}({args_str})[/dim]")


def confirm(message: str) -> bool:
    return Confirm.ask(message)


def stream_text(text: str):
    with Live(console=console, refresh_per_second=20) as live:
        buffer = ""
        for chunk in text.split(" "):
            buffer += chunk + " "
            live.update(Markdown(buffer))
