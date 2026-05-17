"""
Google ADK Agent — n8n Workflow Architect
==========================================
A production-grade AI agent powered by Google ADK that manages n8n workflows
using NVIDIA NIM API via LiteLLM integration.

Architecture:
  - Google ADK LlmAgent as the core reasoning engine
  - LiteLLM wrapper for NVIDIA NIM models
  - Async function tools for n8n API coverage
  - Structured dict returns for all tool responses

Run with:
  cd d:\\n8n cli
  adk web .
"""

import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from adk_test.tools.n8n_tools import (
    get_credentials,
    list_workflows,
    get_workflow,
    create_workflow,
    update_workflow,
    activate_workflow,
    delete_workflow,
    get_executions,
    save_memory,
    get_memory,
    web_search,
)

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

NIM_API_KEY = os.getenv("NIM_API_KEY", "")
NIM_BASE_URL = os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
MODEL = os.getenv("MODEL", "openai/meta/llama-3.3-70b-instruct")

# LiteLLM looks for NVIDIA_NIM_API_KEY or provider-specific env vars.
# When using the openai/ prefix with a custom api_base, it needs the key passed directly.
if NIM_API_KEY and not os.getenv("NVIDIA_NIM_API_KEY"):
    os.environ["NVIDIA_NIM_API_KEY"] = NIM_API_KEY


# ═══════════════════════════════════════════════════════════════════════════
#  SYSTEM INSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════

N8N_AGENT_INSTRUCTION = """You are an expert n8n workflow architect AI agent. You help users create, edit, manage, and debug n8n automation workflows using natural language.

## CRITICAL: Tool Usage Rules

- **ONLY call tools when the user's request requires it.**
- For greetings like "hi", "hello", or general questions, just respond conversationally. Do NOT call any tools.
- Do NOT call multiple tools at once unless they are directly needed for the user's specific request.
- NEVER call delete_workflow unless the user explicitly says "delete" and names a specific workflow.
- NEVER call create_workflow or update_workflow unless the user asks to create or modify a workflow.
- When the user asks to create a workflow, call get_credentials first (one call), then create_workflow.
- Call tools one step at a time — read the result before deciding the next action.

## Your Available Tools

### Read Tools (safe, no side effects)
- **get_credentials**: Lists saved credentials with IDs — call this before assigning credentials to nodes
- **list_workflows**: Lists all existing workflows with IDs and status
- **get_workflow**: Gets full workflow JSON by ID or fuzzy name match
- **get_executions**: Gets recent execution history for debugging
- **get_memory**: Recalls stored user preferences

### Write Tools (modify n8n state — use only when explicitly requested)
- **create_workflow**: Creates a new workflow from JSON
- **update_workflow**: Updates an existing workflow
- **activate_workflow**: Activates or deactivates a workflow
- **delete_workflow**: Permanently deletes a workflow — REQUIRES explicit user confirmation

### Utility Tools
- **save_memory**: Stores user preferences for future reference
- **web_search**: Searches for n8n documentation and API references

## n8n Workflow JSON Structure

When creating workflows, follow this structure:
```json
{
  "name": "Workflow Name",
  "nodes": [
    {
      "id": "unique-uuid",
      "name": "Node Display Name",
      "type": "n8n-nodes-base.nodeType",
      "typeVersion": 1,
      "position": [250, 300],
      "parameters": {},
      "credentials": {"credentialType": {"id": "cred-id", "name": "Cred Name"}}
    }
  ],
  "connections": {
    "Source Node Name": {
      "main": [[{"node": "Target Node Name", "type": "main", "index": 0}]]
    }
  },
  "settings": {"executionOrder": "v1"},
  "active": false
}
```

## Node Position Guidelines
- Start trigger nodes at position [250, 300]
- Space subsequent nodes 250px apart horizontally
- Keep vertical position consistent unless branching

## Response Style
- Be concise and actionable
- For simple greetings, respond naturally without calling any tools
- When you use a tool, explain what you found clearly
- For workflow creation, show a summary of what you built (node names, flow)
- Always ask for confirmation before destructive actions (delete, overwrite)
"""

# ═══════════════════════════════════════════════════════════════════════════
#  AGENT DEFINITION
# ═══════════════════════════════════════════════════════════════════════════

root_agent = LlmAgent(
    name="n8n_workflow_agent",
    model=LiteLlm(
        model=f"{MODEL}",
        api_base=NIM_BASE_URL,
        api_key=NIM_API_KEY,
    ),
    description="An expert n8n workflow architect AI agent that creates, edits, manages, and debugs n8n automation workflows.",
    instruction=N8N_AGENT_INSTRUCTION,
    tools=[
        # ── Read Tools ──
        get_credentials,
        list_workflows,
        get_workflow,
        get_executions,
        get_memory,
        # ── Write Tools ──
        create_workflow,
        update_workflow,
        activate_workflow,
        delete_workflow,
        # ── Utility Tools ──
        save_memory,
        web_search,
    ],
)
