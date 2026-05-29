"""
n8n Developer Subagent
======================
A specialized subagent powered by Google ADK that is dedicated to building,
modifying, activating, and deleting n8n workflows.
"""

import os
from dotenv import load_dotenv

import json

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from n8n_agent.tools import (
    create_workflow,
    update_workflow,
    activate_workflow,
    delete_workflow,
    get_templates,
    get_credentials,
    get_node_summary,
    get_multiple_nodes_summary,
)

# Load environment variables
load_dotenv()

# Load node_index.json to provide it in instructions
try:
    node_index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "node_index.json")
    with open(node_index_path, "r", encoding="utf-8") as f:
        node_index_data = json.load(f)
    # Format list of nodes: just name, displayName, and description to keep it small and clear
    node_index_summary = "\n".join([
        f"- Technical Name: {n.get('name')} | Display Name: {n.get('displayName')} | Description: {n.get('description', '')}"
        for n in node_index_data
    ])
except Exception as e:
    node_index_summary = f"Error loading node_index.json: {e}"


# ── LiteLLM / LLM Provider Configuration ────────────────────────────────────
LITELLM_MODEL = (
    os.getenv("LITELLM_MODEL")
    or os.getenv("MODEL")
    or "openai/gpt-4o-mini"
)
LITELLM_API_BASE = (
    os.getenv("LITELLM_API_BASE")
    or os.getenv("NIM_BASE_URL")
    or os.getenv("API_BASE")
    or "https://api.aicredits.in/v1"
)
LITELLM_API_KEY = (
    os.getenv("LITELLM_API_KEY")
    or os.getenv("NIM_API_KEY")
    or os.getenv("NVIDIA_NIM_API_KEY")
    or os.getenv("API_KEY")

)


DEVELOPER_SUBAGENT_INSTRUCTION = f"""You are a highly specialized n8n Developer Subagent. Your sole responsibility is to design, write, deploy, modify, and fix n8n workflows using n8n JSON.

## Your Available Tools (Writing/Modifying/Reference)
- **create_workflow**: Creates a brand new workflow from an n8n JSON string.
- **update_workflow**: Completely replaces the JSON content of an existing workflow by its ID.
- **activate_workflow**: Activates or deactivates a workflow so it triggers automatically.
- **delete_workflow**: Permanently deletes a workflow (requires clear intention from the main agent).
- **get_templates**: Retrieves standard workflow skeletons to ensure syntax correctness.
- **get_credentials**: Retrieves saved credentials to assign to new nodes.
- **get_node_summary**: Retrieves the lightweight summary schema for a SINGLE node type.
- **get_multiple_nodes_summary**: Retrieves lightweight summaries for MULTIPLE node types in parallel in a single call.

## Critical Task Guidelines:
1. **Node Selection & Parallel Schema Resolution (MANDATORY STEP)**:
   - Identify all necessary node types for the user's task from the **Available Node Types List** below.
   - Call the **get_multiple_nodes_summary** tool with the list of decided node names to retrieve ALL node summaries at the exact same time (in parallel).
   - Alternatively, call `get_node_summary` for a single node if only one is required.
   - Use EXACTLY the parameters, options, and credentials returned in the summaries. Do not hallucinate or guess fields.
2. **Always Use Templates & Credentials**: Before drafting a workflow, inspect standard structures using `get_templates` and check existing credential profiles with `get_credentials` to match saved accounts to target nodes.
3. **Self-Healing Connection Verification**:
   - Connection routing must refer ONLY to node names that physically exist in the workflow's nodes list. Node names are case-sensitive.
   - When calling `create_workflow` or `update_workflow`, a local linter will execute automatically.
   - If a `validation_error` is returned, analyze the broken node connection names, rebuild the connections mapping correctly, and retry the operation.
   - If a `system_error` (connection refused, unauthorized, offline server) is returned, DO NOT retry under any circumstances. Stop execution immediately and report the error description.
4. **Topology Layout**:
   - Start triggers at coordinates `[250, 300]`.
   - Align sequential nodes horizontally, spaced `250px` apart (e.g., node 2 at `[500, 300]`, node 3 at `[750, 300]`).
5. **Summary**: Return a clean summary of what you accomplished (e.g. nodes created, credentials assigned, and workflow status) back to the main agent. Do not converse with the user directly.

## Available Node Types List:
{node_index_summary}
"""

n8n_developer = LlmAgent(
    name="n8n_developer",
    model=LiteLlm(
        model=LITELLM_MODEL,
        api_base=LITELLM_API_BASE,
        api_key=LITELLM_API_KEY,
    ),
    description="A dedicated n8n developer subagent that handles all workflow creation, modification, activation, and deletion tasks.",
    instruction=DEVELOPER_SUBAGENT_INSTRUCTION,
    tools=[
        # ── Write/Modifying Tools ──
        create_workflow,
        update_workflow,
        activate_workflow,
        delete_workflow,
        # ── Helper Reference Tools ──
        get_templates,
        get_credentials,
        get_node_summary,
        get_multiple_nodes_summary,
    ],
)


async def n8n_developer_subagent(prompt: str) -> str:
    """
    Delegate a heavy workflow modification, creation, activation, or deletion task 
    to the specialized n8n Developer Subagent.
    Call this tool when you need to create, update, edit, activate, or delete a workflow.

    Args:
        prompt: A clear, highly specific description of the workflow task that the 
            developer subagent should execute. Detail the desired node configurations, 
            wiring connections, and expected trigger settings.

    Returns:
        A detailed summary text report of the completed workflow operations.
    """
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    # Dynamically instantiate a runner to execute the developer subagent session
    runner = InMemoryRunner(agent=n8n_developer, app_name="n8n_developer_subagent")
    
    session = await runner.session_service.create_session(
        app_name="n8n_developer_subagent",
        user_id="cli_user",
    )
    
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )
    
    from rich.console import Console
    console = Console()
    
    console.print("  [bold yellow]⚙ DELEGATE[/bold yellow] Spawning dedicated [bold bright_magenta]n8n Developer Subagent[/bold bright_magenta]...")
    
    final_text = []
    active_tool = None
    
    async for event in runner.run_async(
        user_id="cli_user",
        session_id=session.id,
        new_message=user_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    fc = part.function_call
                    active_tool = fc.name
                    args_summary = ""
                    if fc.args:
                        args_list = [f"{k}={str(v)[:30]}..." if len(str(v)) > 30 else f"{k}={v}" for k, v in fc.args.items()]
                        args_summary = f" [dim]({', '.join(args_list)})[/dim]"
                    console.print(f"    [bold bright_magenta]⚙ SUB-TOOL[/bold bright_magenta] Running [bold bright_cyan]{fc.name}[/bold bright_cyan]{args_summary}...")
                elif part.function_response:
                    fr = part.function_response
                    result_str = str(fr.response) if fr.response else ""
                    if len(result_str) > 100:
                        result_str = result_str[:97] + "..."
                    console.print(f"    [bold green]✔ SUB-DONE[/bold green] Completed [dim]{active_tool or 'operation'}[/dim] [green]-> {result_str}[/green]")
                    active_tool = None
                elif part.text:
                    final_text.append(part.text)
                    
    console.print("  [bold green]✔ REPORT[/bold green] Subagent finished operations successfully.\n")
    return "".join(final_text) if final_text else "Subagent completed execution with no response report."
