"""
n8n CLI — Powered by Google ADK Agent
=======================================
Main entry point that runs the ADK-based n8n workflow agent.

Supports two modes:
  1. Interactive CLI (default): `python main.py`
  2. ADK Dev UI:                `adk web .`
"""

import asyncio
import sys
import os
import time

# Ensure the project root is on sys.path so adk_test is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[1/5] Loading environment variables...")
from dotenv import load_dotenv

# Load the adk_test/.env first (has the NIM keys), then root .env as fallback
load_dotenv(os.path.join(os.path.dirname(__file__), "adk_test", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)

# ── Prevent ADK from hanging on Google API initialization ──────────────────
# The ADK internally initializes google.genai which tries to validate
# credentials with Google servers. Since we use LiteLLM + NVIDIA NIM,
# the Google API key is never actually used — but we need a placeholder
# to prevent the initialization from hanging/blocking.
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "not-used-with-litellm"

# Suppress noisy LiteLLM warnings about missing AWS modules
os.environ.setdefault("LITELLM_LOG", "ERROR")

print("[2/5] Loading Rich console...")
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

print("[3/5] Loading Google ADK (this may take 30-60s on first run)...")
t0 = time.time()
from google.adk.runners import InMemoryRunner
from google.genai import types
print(f"      ADK loaded in {time.time() - t0:.1f}s")

print("[4/5] Importing ADK agent & tools...")
t0 = time.time()
from adk_test.agent import root_agent
print(f"      Agent loaded in {time.time() - t0:.1f}s")

print("[5/5] Ready!\n")


# ═══════════════════════════════════════════════════════════════════════════
#  INTERACTIVE CLI RUNNER
# ═══════════════════════════════════════════════════════════════════════════


async def run_interactive():
    """Run the ADK agent in an interactive CLI loop."""

    console.print(
        Panel.fit(
            "[bold cyan]n8n Workflow Agent[/bold cyan]\n"
            "[dim]Powered by Google ADK + NVIDIA NIM (Llama 3.3 70B)[/dim]\n\n"
            "[green]Type your request to create, edit, or manage n8n workflows.[/green]\n"
            "[dim]Type 'quit' or 'exit' to stop.[/dim]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )

    # Create the InMemoryRunner with our ADK agent
    runner = InMemoryRunner(agent=root_agent, app_name="n8n_cli")

    # Create a session for this conversation
    session = await runner.session_service.create_session(
        app_name="n8n_cli",
        user_id="cli_user",
    )

    session_id = session.id
    console.print(f"[dim]Session: {session_id}[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold yellow]You > [/bold yellow]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        # Build the user message content
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        )

        console.print("[dim]Thinking...[/dim]")

        # Run the agent and collect responses
        final_response_parts = []
        tool_calls_shown = set()

        try:
            async for event in runner.run_async(
                user_id="cli_user",
                session_id=session_id,
                new_message=user_content,
            ):
                # event is a google.adk.events.Event
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # Show tool calls as they happen
                        if part.function_call:
                            fc = part.function_call
                            call_key = f"{fc.name}:{id(part)}"
                            if call_key not in tool_calls_shown:
                                tool_calls_shown.add(call_key)
                                args_str = ""
                                if fc.args:
                                    args_items = []
                                    for k, v in fc.args.items():
                                        v_str = str(v)
                                        if len(v_str) > 100:
                                            v_str = v_str[:97] + "..."
                                        args_items.append(f"{k}={v_str}")
                                    args_str = ", ".join(args_items)
                                console.print(
                                    f"  [cyan]⚡ Tool:[/cyan] [bold]{fc.name}[/bold]"
                                    f"({args_str})"
                                )

                        # Show tool results
                        elif part.function_response:
                            fr = part.function_response
                            result_str = str(fr.response) if fr.response else ""
                            if len(result_str) > 200:
                                result_str = result_str[:197] + "..."
                            console.print(
                                f"  [green]✓ Result:[/green] [dim]{result_str}[/dim]"
                            )

                        # Collect final text response
                        elif part.text:
                            final_response_parts.append(part.text)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()
            console.print()
            continue

        # Display the final agent response
        if final_response_parts:
            full_response = "".join(final_response_parts)
            console.print()
            console.print(
                Panel(
                    Markdown(full_response),
                    title="[bold bright_cyan]Agent[/bold bright_cyan]",
                    border_style="bright_cyan",
                    padding=(1, 2),
                )
            )
        else:
            console.print("[dim]No response from agent.[/dim]")

        console.print()


# ═══════════════════════════════════════════════════════════════════════════
#  SINGLE-SHOT MODE (for scripting / piping)
# ═══════════════════════════════════════════════════════════════════════════


async def run_single(message: str):
    """Run the ADK agent with a single message and print the response."""
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
    async for event in runner.run_async(
        user_id="cli_user",
        session_id=session.id,
        new_message=user_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text.append(part.text)

    print("".join(final_text))


# ═══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════


def main():
    """
    Main entry point.

    Usage:
      python main.py                     # Interactive CLI mode
      python main.py "list my workflows"  # Single-shot mode
      adk web .                           # ADK Dev UI (uses adk_test/agent.py directly)
    """
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        asyncio.run(run_single(message))
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
