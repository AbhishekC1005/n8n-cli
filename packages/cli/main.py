import json
import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt

from config import settings, ensure_agent_home
from n8n.client import client
from packages.cli.display import (
    show_spinner,
    show_error,
    show_success,
    show_table,
    confirm,
    stream_text,
)
from packages.cli.session import (
    load_session,
    save_turn,
    clear_session,
    get_session_id,
    archive_old_sessions,
)
from packages.cli.commands.list import list_workflows_cmd
from packages.cli.commands.history import show_history_cmd
from packages.cli.commands.restore import restore_workflow_cmd
from packages.cli.commands.memory import show_memory_cmd
from core.agent import run_agent
from core.tools import execute_tool
from storage import init_db

console = Console()
app = typer.Typer(help="AI-powered n8n workflow builder")


def get_workflow_url(workflow_id: str) -> str:
    return f"{settings.N8N_BASE_URL}/workflow/{workflow_id}"


async def process_slash_command(cmd: str, messages: list) -> bool:
    parts = cmd.strip().split()
    command = parts[0].lower()

    if command == "/list":
        await list_workflows_cmd()
        return True
    elif command == "/history":
        await show_history_cmd()
        return True
    elif command == "/restore" and len(parts) > 1:
        await restore_workflow_cmd(parts[1])
        return True
    elif command == "/memory":
        await show_memory_cmd()
        return True
    elif command == "/clear":
        clear_session()
        messages.clear()
        console.print("[green]Session cleared.[/green]")
        return True
    elif command == "/compact":
        from core.context import trim_history

        messages[:] = await trim_history(messages)
        console.print("[green]History compacted.[/green]")
        return True
    elif command == "/cost":
        from core.context import estimate_tokens

        total = sum(estimate_tokens(str(m.get("content", ""))) for m in messages)
        console.print(
            f"[dim]Estimated tokens in session: {total} (~${(total / 1000) * 0.03:.4f})[/dim]"
        )
        return True
    elif command == "/dry-run":
        console.print("[yellow]Dry-run mode: changes will not be applied[/yellow]")
        return True
    elif command.startswith("/edit") and len(parts) > 1:
        name = " ".join(parts[1:])
        with show_spinner(f"Loading workflow '{name}'..."):
            wf_json = await execute_tool("get_workflow", {"id_or_name": name})
        if wf_json and "not found" not in wf_json.lower():
            messages.append(
                {"role": "user", "content": f"Edit this workflow: {wf_json}"}
            )
            console.print(f"[green]Loaded workflow context.[/green]")
        return True
    elif command.startswith("/activate") and len(parts) > 1:
        name = " ".join(parts[1:])
        wf_json = await execute_tool("get_workflow", {"id_or_name": name})
        if wf_json:
            wf_data = json.loads(wf_json)
            wf_id = wf_data.get("id", "")
            result = await execute_tool(
                "activate_workflow", {"workflow_id": wf_id, "active": True}
            )
            console.print(f"[green]{result}[/green]")
        return True
    elif command.startswith("/deactivate") and len(parts) > 1:
        name = " ".join(parts[1:])
        wf_json = await execute_tool("get_workflow", {"id_or_name": name})
        if wf_json:
            wf_data = json.loads(wf_json)
            wf_id = wf_data.get("id", "")
            result = await execute_tool(
                "activate_workflow", {"workflow_id": wf_id, "active": False}
            )
            console.print(f"[green]{result}[/green]")
        return True

    return False


async def chat_loop():
    messages = load_session()
    archive_old_sessions()

    console.print("[bold blue]n8n-agent[/bold blue] - AI-powered workflow builder")
    console.print(
        "[dim]Type /help for commands, /clear to reset, Ctrl+C to exit[/dim]\n"
    )

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            handled = await process_slash_command(user_input, messages)
            if not handled:
                console.print(f"[dim]Unknown command: {user_input}[/dim]")
            continue

        save_turn("user", user_input)
        messages.append({"role": "user", "content": user_input})

        try:
            response = await run_agent(user_input, messages)
            console.print(f"\n[bold blue]Agent:[/bold blue] {response}\n")
        except Exception as e:
            show_error(f"Agent error: {e}")
            messages.append({"role": "assistant", "content": f"Error: {e}"})


async def one_shot(prompt: str):
    messages = []
    messages.append({"role": "user", "content": prompt})
    save_turn("user", prompt)
    try:
        response = await run_agent(prompt, messages)
        console.print(response)
    except Exception as e:
        show_error(f"Error: {e}")


@app.command()
def chat():
    asyncio.run(chat_loop())


@app.command()
def list():
    asyncio.run(list_workflows_cmd())


@app.command()
def history():
    asyncio.run(show_history_cmd())


@app.command()
def restore(workflow_id: str):
    asyncio.run(restore_workflow_cmd(workflow_id))


@app.command()
def memory():
    asyncio.run(show_memory_cmd())


@app.command()
def edit(name: str):
    async def _edit():
        messages = load_session()
        with show_spinner(f"Loading workflow '{name}'..."):
            wf_json = await execute_tool("get_workflow", {"id_or_name": name})
        if wf_json and "not found" not in wf_json.lower():
            messages.append(
                {"role": "user", "content": f"Edit this workflow: {wf_json}"}
            )
            console.print(f"[green]Loaded workflow '{name}'. Start chatting.[/green]\n")
            while True:
                try:
                    user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
                except (KeyboardInterrupt, EOFError):
                    break
                if not user_input:
                    continue
                if user_input.startswith("/"):
                    await process_slash_command(user_input, messages)
                    continue
                save_turn("user", user_input)
                messages.append({"role": "user", "content": user_input})
                response = await run_agent(
                    user_input, messages, workflow_context=wf_json
                )
                console.print(f"\n[bold blue]Agent:[/bold blue] {response}\n")

    asyncio.run(_edit())


@app.command()
def cost():
    messages = load_session()
    from core.context import estimate_tokens

    total = sum(estimate_tokens(str(m.get("content", ""))) for m in messages)
    console.print(
        f"[dim]Estimated tokens in session: {total} (~${(total / 1000) * 0.03:.4f})[/dim]"
    )


@app.command()
def main(prompt: Optional[str] = typer.Argument(None)):
    if prompt:
        asyncio.run(one_shot(prompt))
    else:
        asyncio.run(chat_loop())


if __name__ == "__main__":
    app()
