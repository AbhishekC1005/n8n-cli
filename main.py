"""
n8n CLI — Powered by Google ADK Agent
=======================================
Main entry point that runs the ADK-based n8n workflow agent.

Supports two modes:
  1. Interactive CLI (default): `n8n-agent` or `python main.py`
  2. Single-shot Command:       `n8n-agent "list my workflows"`
"""

import asyncio
import sys
import os
import time

# Ensure the project root is on sys.path so n8n_agent is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force standard output and error streams to use UTF-8, avoiding emoji crashes on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass


from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.box import ROUNDED

console = Console()

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION & ENVIRONMENT CHECKS
# ═══════════════════════════════════════════════════════════════════════════

def check_configuration():
    """Check if environment credentials are loaded correctly, otherwise print error and exit."""
    # Load .env first
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    
    n8n_key = os.getenv("N8N_API_KEY")
    
    # Verify at least one LLM api key exists (supporting LiteLLM, Gemini, or NIM configurations)
    llm_key = (
        os.getenv("LITELLM_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("NIM_API_KEY")
        or os.getenv("NVIDIA_NIM_API_KEY")
        or os.getenv("API_KEY")
    )
    
    if not n8n_key:
        console.print(
            "\n[bold red]ERROR: Missing N8N_API_KEY environment credential.[/bold red]\n"
            "Please ensure your [bold]N8N_API_KEY[/bold] is configured in your [bold].env[/bold] file.\n"
            "Exiting...\n"
        )
        sys.exit(1)
        
    if not llm_key:
        console.print(
            "\n[bold red]ERROR: Missing LLM API key credential.[/bold red]\n"
            "Please configure [bold]LITELLM_API_KEY[/bold] or [bold]GEMINI_API_KEY[/bold] in your [bold].env[/bold] file to authenticate the AI model.\n"
            "Exiting...\n"
        )
        sys.exit(1)
        
    # Ensure keys are set in environment for Google GenAI client if using Gemini
    current_gemini = os.getenv("GEMINI_API_KEY")
    if current_gemini:
        os.environ["GEMINI_API_KEY"] = current_gemini
        os.environ["GOOGLE_API_KEY"] = current_gemini
    os.environ.setdefault("LITELLM_LOG", "ERROR")


# Run config check immediately on import/run
check_configuration()

# ── Import ADK and Tools after loading Env ──────────────────────────────────
from google.adk.runners import InMemoryRunner
from google.genai import types
from n8n_agent.agent import root_agent
from n8n_agent.client import n8n


# ═══════════════════════════════════════════════════════════════════════════
#  SLASH COMMANDS ROUTER
# ═══════════════════════════════════════════════════════════════════════════

async def handle_slash_command(command_str: str) -> bool:
    """
    Handle a slash command directly, bypassing LLM reasoning.
    Returns True if the shell loop should continue, False to exit.
    """
    parts = command_str.strip().split()
    cmd = parts[0].lower()
    args = parts[1:]
    
    if cmd in ("/exit", "/quit"):
        console.print("[dim]Goodbye![/dim]")
        return False
        
    elif cmd == "/clear":
        console.clear()
        return True
        
    elif cmd == "/help":
        console.print(
            Panel(
                "[bold bright_cyan]n8n-agent CLI Commands Reference[/bold bright_cyan]\n\n"
                "  [bold yellow]/list[/bold yellow]                 - List all workflows on n8n instance\n"
                "  [bold yellow]/get <id>[/bold yellow]             - Retrieve full JSON schema of a workflow\n"
                "  [bold yellow]/activate <id>[/bold yellow]        - Activate a workflow to execute automatically\n"
                "  [bold yellow]/deactivate <id>[/bold yellow]      - Deactivate a workflow\n"
                "  [bold yellow]/history[/bold yellow]             - View recent workflow execution run logs\n"
                "  [bold yellow]/clear[/bold yellow]               - Clear the terminal screen\n"
                "  [bold yellow]/exit[/bold yellow] or [bold yellow]/quit[/bold yellow]      - Close the interactive shell\n\n"
                "[dim]For custom operations, just describe your automation task in natural language.[/dim]",
                title="[bold cyan]Help Manual[/bold cyan]",
                border_style="bright_cyan"
            )
        )
        return True
        
    elif cmd == "/list":
        with console.status("[bold cyan]Contacting n8n instance...[/bold cyan]"):
            try:
                workflows = await n8n.get_workflows()
                if not workflows:
                    console.print("[yellow]No workflows found on this instance.[/yellow]")
                    return True
                
                table = Table(
                    title="[bold bright_magenta]n8n Active Workflows[/bold bright_magenta]",
                    box=ROUNDED,
                    header_style="bold bright_cyan",
                    border_style="bright_blue",
                )
                table.add_column("ID", style="dim", justify="center")
                table.add_column("Name", style="bold white")
                table.add_column("Status", style="cyan", justify="center")
                table.add_column("Nodes", style="magenta", justify="center")
                
                for wf in workflows:
                    node_count = len(wf.get("nodes", []))
                    status_text = "[bold green]● Active[/bold green]" if wf.get("active") else "[bold dim red]○ Inactive[/bold dim red]"
                    table.add_row(
                        wf.get("id", ""),
                        wf.get("name", "Untitled"),
                        status_text,
                        str(node_count)
                    )
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error listing workflows: {e}[/red]")
        return True
        
    elif cmd == "/get":
        if not args:
            console.print("[red]Usage: /get <workflow_id>[/red]")
            return True
        wf_id = args[0]
        with console.status(f"[bold cyan]Fetching workflow {wf_id}...[/bold cyan]"):
            try:
                wf = await n8n.get_workflow(wf_id)
                console.print_json(data=wf)
            except Exception as e:
                console.print(f"[red]Error fetching workflow details: {e}[/red]")
        return True
        
    elif cmd == "/activate":
        if not args:
            console.print("[red]Usage: /activate <workflow_id>[/red]")
            return True
        wf_id = args[0]
        with console.status(f"[bold cyan]Activating workflow {wf_id}...[/bold cyan]"):
            try:
                res = await n8n.activate_workflow(wf_id)
                console.print(f"[green]✓ Workflow '{res.get('name', wf_id)}' activated successfully![/green]")
            except Exception as e:
                console.print(f"[red]Error activating workflow: {e}[/red]")
        return True
        
    elif cmd == "/deactivate":
        if not args:
            console.print("[red]Usage: /deactivate <workflow_id>[/red]")
            return True
        wf_id = args[0]
        with console.status(f"[bold cyan]Deactivating workflow {wf_id}...[/bold cyan]"):
            try:
                res = await n8n.deactivate_workflow(wf_id)
                console.print(f"[green]✓ Workflow '{res.get('name', wf_id)}' deactivated successfully![/green]")
            except Exception as e:
                console.print(f"[red]Error deactivating workflow: {e}[/red]")
        return True
        
    elif cmd == "/history":
        limit = 10
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                pass
        with console.status("[bold cyan]Fetching execution runs...[/bold cyan]"):
            try:
                history = await n8n.get_executions(limit=limit)
                if not history:
                    console.print("[yellow]No execution logs found.[/yellow]")
                    return True
                
                table = Table(
                    title=f"[bold bright_magenta]Recent Executions (Limit {limit})[/bold bright_magenta]",
                    box=ROUNDED,
                    header_style="bold bright_cyan",
                    border_style="bright_blue"
                )
                table.add_column("Execution ID", style="dim", justify="center")
                table.add_column("Workflow ID", style="magenta", justify="center")
                table.add_column("Status", style="bold", justify="center")
                table.add_column("Started At", style="cyan")
                table.add_column("Duration", style="yellow", justify="right")
                
                for run in history:
                    is_success = run.get("finished") and run.get("status") == "success"
                    status_text = "[bold green]✔ success[/bold green]" if is_success else f"[bold red]✘ {run.get('status', 'failed')}[/bold red]"
                    table.add_row(
                        run.get("id", ""),
                        run.get("workflowId", ""),
                        status_text,
                        run.get("startedAt", "")[:19].replace("T", " "),
                        f"{run.get('executionTime', 0)}ms"
                    )
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching execution history: {e}[/red]")
        return True
        
    else:
        console.print(f"[red]Unknown slash command: {cmd}. Type /help for assistance.[/red]")
        return True


# ═══════════════════════════════════════════════════════════════════════════
#  STATEFUL INTERACTIVE CLI RUNNER
# ═══════════════════════════════════════════════════════════════════════════

async def run_interactive():
    """Run the ADK agent in a premium interactive stateful shell loop."""
    from prompt_toolkit import PromptSession, HTML
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.completion import WordCompleter
    from rich.align import Align
    from rich.box import ROUNDED
    
    n8n_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    
    # Premium compact 3-line block ASCII art for N8N AGENT
    logo = (
        "\n"
        "  [bold bright_magenta]█▄  █  ▄▀▀▄  █▄  █[/bold bright_magenta]   [bold bright_cyan]▄▀▀▄  ▄▀▀▀  █▀▀▀  █▄  █  ▀▀█▀▀[/bold bright_cyan]\n"
        "  [bold bright_magenta]█ ▀▄█  █▄▄█  █ ▀▄█[/bold bright_magenta]   [bold bright_cyan]█▄▄█  █ ▀█  █▀▀   █ ▀▄█    █  [/bold bright_cyan]\n"
        "  [bold bright_magenta]█   █  ▀▄▄▀  █   █[/bold bright_magenta]   [bold bright_cyan]█  █  ▀▄▄▀  █▄▄▄  █   █    █  [/bold bright_cyan]\n\n"
        f"  [bold green]● Active[/bold green]  [dim]|[/dim]  [bold bright_cyan]Connected to n8n[/bold bright_cyan] [dim]({n8n_url})[/dim]\n"
        "  [dim]────────────────────────────────────────────────────────────────────────[/dim]\n"
        "   • [bold white]Chat & Define[/bold white]   : Ask natural language questions about triggers & APIs\n"
        "   • [bold white]Workflow Dev[/bold white]    : Ask to [bold bright_magenta]create, update, activate[/bold bright_magenta], or [bold bright_magenta]delete[/bold bright_magenta] workflows\n"
        "   • [bold white]Slash Actions[/bold white]   : Type [bold yellow]/list[/bold yellow], [bold yellow]/history[/bold yellow], [bold yellow]/get <id>[/bold yellow], [bold yellow]/help[/bold yellow], or [bold yellow]/clear[/bold yellow]\n"
    )
    
    console.print(
        Panel(
            Align.left(logo),
            box=ROUNDED,
            border_style="bright_magenta",
            padding=(0, 2),
            expand=False
        )
    )

    # Instantiate the prompt-toolkit stateful session
    history_file = os.path.join(os.path.dirname(__file__), ".n8n_agent_history")
    prompt_session = PromptSession(history=FileHistory(history_file))
    
    # Simple dropdown autocompleter for slash commands
    completer = WordCompleter([
        "/help", "/list", "/get", "/activate", "/deactivate", "/history", "/clear", "/exit", "/quit"
    ], ignore_case=True)

    # Initialize Google ADK runner
    runner = InMemoryRunner(agent=root_agent, app_name="n8n_cli")
    session = await runner.session_service.create_session(
        app_name="n8n_cli",
        user_id="cli_user",
    )
    
    session_id = session.id
    console.print(f"[dim]Active Agent Session: {session_id}[/dim]\n")

    while True:
        try:
            # Multi-line/history prompt with styled HTML prompt caretaker
            user_input = await prompt_session.prompt_async(
                HTML('<brightmagenta><b>n8n-agent</b></brightmagenta> <white>❯</white> '),
                completer=completer
            )
            user_input = user_input.strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        # Handle direct slash commands
        if user_input.startswith("/"):
            continue_loop = await handle_slash_command(user_input)
            if not continue_loop:
                break
            console.print()
            continue

        # Normal text triggers LLM conversation
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        )

        final_response_parts = []
        tool_calls_shown = set()
        has_printed_response_header = False

        from rich.live import Live
        from rich.markdown import Markdown

        status = console.status("[bold cyan]Agent is thinking...[/bold cyan]")
        status_active = True
        status.start()
        
        live = None

        try:
            async for event in runner.run_async(
                user_id="cli_user",
                session_id=session_id,
                new_message=user_content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # Show tool invocations dynamically
                        if part.function_call:
                            if live:
                                live.stop()
                                live = None
                            
                            fc = part.function_call
                            call_key = f"{fc.name}:{id(part)}"
                            if call_key not in tool_calls_shown:
                                tool_calls_shown.add(call_key)
                                args_str = ""
                                if fc.args:
                                    args_items = []
                                    for k, v in fc.args.items():
                                        v_str = str(v)
                                        if len(v_str) > 60:
                                            v_str = v_str[:57] + "..."
                                        args_items.append(f"{k}={v_str}")
                                    args_str = ", ".join(args_items)
                                
                                if not status_active:
                                    status.start()
                                    status_active = True
                                status.update(f"[bold yellow]Executing {fc.name}...[/bold yellow]")
                                console.print(
                                    f"  [bold bright_magenta]⚙ TOOL[/bold bright_magenta] [bold bright_cyan]{fc.name}[/bold bright_cyan] [dim]{args_str}[/dim]"
                                )

                        # Show tool response results
                        elif part.function_response:
                            if live:
                                live.stop()
                                live = None
                                
                            fr = part.function_response
                            result_str = str(fr.response) if fr.response else ""
                            if len(result_str) > 100:
                                result_str = result_str[:97] + "..."
                            
                            if not status_active:
                                status.start()
                                status_active = True
                            console.print(
                                f"  [bold green]✔ DONE[/bold green] [dim]{result_str}[/dim]"
                            )
                            status.update("[bold cyan]Agent is thinking...[/bold cyan]")

                        # Collect and stream generated response pieces
                        elif part.text:
                            if status_active:
                                status.stop()
                                status_active = False
                            
                            if not has_printed_response_header:
                                console.print("\n[bold bright_magenta]n8n-agent[/bold bright_magenta] [white]❯[/white] ")
                                has_printed_response_header = True
                                live = Live(Markdown(""), console=console, auto_refresh=True, vertical_overflow="visible")
                                live.start()
                            
                            final_response_parts.append(part.text)
                            if live:
                                live.update(Markdown("".join(final_response_parts)))

        except Exception as e:
            if status_active:
                status.stop()
                status_active = False
            if live:
                live.stop()
                live = None
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()
            console.print()
            continue
        finally:
            if status_active:
                status.stop()
            if live:
                live.stop()

        if not final_response_parts:
            console.print("[dim]No response from agent.[/dim]")

        console.print()


# ═══════════════════════════════════════════════════════════════════════════
#  SINGLE-SHOT CONSOLE RUNNER
# ═══════════════════════════════════════════════════════════════════════════

async def run_single(message: str):
    """Run the ADK agent with a single instruction and output the raw response."""
    runner = InMemoryRunner(agent=root_agent, app_name="n8n_cli")
    session = await runner.session_service.create_session(
        app_name="n8n_cli",
        user_id="cli_user",
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )

    final_text = []
    
    with console.status("[bold cyan]Executing single instruction...[/bold cyan]"):
        async for event in runner.run_async(
            user_id="cli_user",
            session_id=session.id,
            new_message=user_content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text.append(part.text)

    console.print(Markdown("".join(final_text)))


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    Main entry point.
    Usage:
      n8n-agent                    # Interactive premium shell
      n8n-agent "list workflows"   # Single-shot scriptable command
    """
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        asyncio.run(run_single(message))
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
