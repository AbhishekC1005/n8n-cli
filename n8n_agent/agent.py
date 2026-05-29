"""
Google ADK Agent — n8n Workflow Architect
==========================================
A hybrid multi-agent system powered by Google ADK that manages n8n workflows
using NVIDIA NIM API via LiteLLM integration.
"""

import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm

# Direct Read-Only and Utility Tools used by conversational Main Agent
from n8n_agent.tools import (
    get_credentials,
    list_workflows,
    get_workflow,
    get_executions,
    get_execution_details,
    save_memory,
    get_memory,
    web_search,
    get_node_summary,
    get_multiple_nodes_summary,
)

# Imported delegated write tool from separate subagent module
from n8n_agent.developer import n8n_developer_subagent

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Ensure key is set in environment for Google GenAI client
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

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



# ═══════════════════════════════════════════════════════════════════════════
#  MAIN AGENT DEFINITION: n8n_workflow_agent (Conversational & Read Router)
# ═══════════════════════════════════════════════════════════════════════════

MAIN_AGENT_INSTRUCTION = """You are the lead n8n Workflow Architect AI Agent. You serve as the main companion for the user, handling conversational chat and routing technical operations.

## CRITICAL Routing Guidelines:

1. **Conversational Questions / Greetings**:
   - If the user says *"hi"*, *"hello"*, or asks conversational questions (e.g., *"how do I set up a Slack credential?"*, *"explain how webhooks work"*), simply answer directly in natural language.
   - **NEVER** call any tools or delegate to your subagent for general conversational queries.

2. **Read-Only Status Lookups (High-Speed Local Execution)**:
   - For all read-only, status, or search actions, call your direct tools immediately. Do NOT delegate these to your subagent.
   - Use **list_workflows** to list existing workflows on the n8n instance.
   - Use **get_workflow** to fetch full JSON details of a workflow.
   - Use **get_executions** to show recent execution runs.
   - Use **get_execution_details** to diagnose failures in specific execution runs.
   - Use **get_credentials** to check existing credential accounts.
   - Use **get_node_summary** to inspect parameters, credentials, and settings for a single specific node type.
   - Use **get_multiple_nodes_summary** to inspect parameters and settings for multiple node types in parallel.
   - Use **web_search** to query external n8n node documentation.
   - Use **get_memory** / **save_memory** to manage user preferences.

3. **Write / Modify Operations (Spawning the Subagent)**:
   - If the user asks you to **create a workflow, edit a workflow, modify parameters, activate/deactivate triggers, or delete a workflow**, you MUST delegate this entire request to your subagent using your tool: **n8n_developer_subagent**.
   - Call the `n8n_developer_subagent` tool with a highly specific description of the workflow task the user wants to accomplish.
   - Once the subagent returns its report, review it and present the final deployment status cleanly to the user.

## Response Style:
- Be professional, encouraging, and highly technical.
- Render workflow structures and execution histories in clean markdown formats.
- Ask for explicit user confirmation before executing any destructive operations (like deleting workflows).
"""

root_agent = LlmAgent(
    name="n8n_workflow_agent",
    model=LiteLlm(
        model=LITELLM_MODEL,
        api_base=LITELLM_API_BASE,
        api_key=LITELLM_API_KEY,
    ),
    description="The primary conversational agent companion that handles lookup queries directly and delegates modification actions to n8n_developer.",
    instruction=MAIN_AGENT_INSTRUCTION,
    tools=[
        # ── Direct Read-Only Tools (High-Speed Local Resolution) ──
        list_workflows,
        get_workflow,
        get_executions,
        get_execution_details,
        get_credentials,
        get_node_summary,
        get_multiple_nodes_summary,
        get_memory,
        save_memory,
        web_search,
        # ── Specialized Subagent Tool (Delegated Write Operations) ──
        n8n_developer_subagent,
    ],
)

