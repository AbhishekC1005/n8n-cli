from rich.console import Console
from rich.panel import Panel

from storage.memory import get_memory

console = Console()


async def show_memory_cmd():
    memory = get_memory()
    if not memory:
        console.print(
            Panel("No stored preferences.", title="Memory", border_style="yellow")
        )
        return

    lines = ["[bold]Stored Preferences:[/bold]\n"]
    for key, value in memory.items():
        lines.append(f"  [cyan]{key}[/cyan]: {value}")

    console.print(Panel("\n".join(lines), title="Memory", border_style="blue"))
