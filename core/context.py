import re
from typing import Optional

from storage.memory import get_memory
from storage.cache import get_cached_nodes
from n8n.client import client
from n8n.schemas import NodeInfo


SERVICE_KEYWORDS = {
    "slack": ["n8n-nodes-slack"],
    "gmail": ["n8n-nodes-gmail"],
    "google": ["n8n-nodes-google"],
    "github": ["n8n-nodes-github"],
    "stripe": ["n8n-nodes-stripe"],
    "webhook": ["n8n-nodes-webhook"],
    "http": ["n8n-nodes-http"],
    "telegram": ["n8n-nodes-telegram"],
    "airtable": ["n8n-nodes-airtable"],
    "notion": ["n8n-nodes-notion"],
    "discord": ["n8n-nodes-discord"],
    "sftp": ["n8n-nodes-sftp"],
    "ftp": ["n8n-nodes-ftp"],
    "mysql": ["n8n-nodes-mysql"],
    "postgres": ["n8n-nodes-postgres"],
    "mongo": ["n8n-nodes-mongodb"],
    "redis": ["n8n-nodes-redis"],
    "aws": ["n8n-nodes-aws"],
    "salesforce": ["n8n-nodes-salesforce"],
    "zendesk": ["n8n-nodes-zendesk"],
    "shopify": ["n8n-nodes-shopify"],
    "mailchimp": ["n8n-nodes-mailchimp"],
}


async def get_relevant_node_schemas(message: str) -> list[NodeInfo]:
    nodes = await get_cached_nodes()
    if not nodes:
        try:
            nodes = await client.get_installed_nodes()
        except Exception:
            return []

    message_lower = message.lower()
    relevant_types = set()

    for keyword, type_prefixes in SERVICE_KEYWORDS.items():
        if keyword in message_lower:
            relevant_types.update(type_prefixes)

    if not relevant_types:
        return nodes[:10]

    return [
        n for n in nodes if any(n.name.startswith(prefix) for prefix in relevant_types)
    ]


async def build_context(user_message: str) -> dict:
    memory = get_memory()
    nodes = await get_relevant_node_schemas(user_message)

    creds = await client.get_credentials()

    return {
        "memory": memory,
        "relevant_nodes": nodes,
        "credentials": creds,
        "user_message": user_message,
    }


def estimate_tokens(text: str) -> int:
    return len(text) // 4


async def trim_history(messages: list, max_tokens: int = 120000) -> list:
    total_tokens = sum(estimate_tokens(str(m.get("content", ""))) for m in messages)
    if total_tokens < max_tokens * 0.8:
        return messages

    keep_count = min(10, len(messages))
    kept = messages[-keep_count:]
    trimmed = messages[:-keep_count]

    summary = f"[Summary of {len(trimmed)} earlier turns]: User discussed workflow modifications and tool usage."
    kept.insert(
        0,
        {
            "role": "system",
            "content": summary,
            "tool_calls": None,
            "tool_results": None,
        },
    )

    return kept


def compress_workflow_in_history(messages: list) -> list:
    compressed = []
    for msg in messages:
        content = msg.get("content", "")
        if (
            isinstance(content, str)
            and "workflow" in content.lower()
            and len(content) > 500
        ):
            compressed_msg = {**msg, "content": "[Workflow JSON compressed]"}
            compressed.append(compressed_msg)
        else:
            compressed.append(msg)
    return compressed
