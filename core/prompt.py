from datetime import datetime
from typing import Optional

from storage.memory import format_for_prompt
from n8n.node_parser import parse_node_schema


SYSTEM_PROMPT_TEMPLATE = """You are an expert n8n workflow architect. You help users create and edit n8n workflows using natural language.

## Strict Rules

1. When generating a workflow, return ONLY valid JSON with no markdown fences, no explanation mixed in
2. Always call get_installed_nodes before generating any new workflow
3. Always call get_credentials before assigning credentials to nodes
4. Use web_search if unsure about a third party API's parameters
5. Validate every workflow before sending to n8n

## n8n Workflow JSON Structure

A workflow has this structure:
```json
{{
  "name": "Workflow Name",
  "nodes": [
    {{
      "id": "unique-id-1",
      "name": "Node Name",
      "type": "n8n-nodes-nodeType",
      "typeVersion": 1.0,
      "position": {{"x": 100, "y": 200}},
      "parameters": {{...}},
      "credentials": {{"credentialName": {{"id": "cred-id", "name": "Cred Name"}}}}
    }}
  ],
  "connections": {{
    "Node Name": {{
      "main": [[{{"node": "Next Node Name", "type": "main", "index": 0}}]]
    }}
  }},
  "settings": {{"executionOrder": "v1"}},
  "active": false
}}
```

## Installed Node Types

{installed_nodes}

## Available Credentials

{credentials}

## User Preferences

{memory}

## Current Time: {current_time}

{workflow_context}
"""


async def build_system_prompt(
    user_message: str,
    relevant_nodes: list,
    credentials: list,
    memory: dict,
    workflow_context: Optional[str] = None,
) -> str:
    node_list = "\n".join([f"- {n.name}: {n.displayName}" for n in relevant_nodes[:30]])

    cred_list = (
        "\n".join([f"- {c.id}: {c.name} ({c.type})" for c in credentials])
        or "No credentials configured"
    )

    memory_str = format_for_prompt()

    context_str = (
        f"\n\n## Workflow Being Edited\n\n{workflow_context}\n\n"
        if workflow_context
        else ""
    )

    return SYSTEM_PROMPT_TEMPLATE.format(
        installed_nodes=node_list,
        credentials=cred_list,
        memory=memory_str,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
        workflow_context=context_str,
    )
