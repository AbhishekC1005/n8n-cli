"""
get_node_summary tool for retrieving lightweight node parameter schemas from the local nodes database.
"""

import os
import json
from typing import Optional

# Path to the full node schemas file
_NODES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "nodes.json")

# Lazy-loaded cache
_nodes_cache: Optional[dict] = None


def _load_nodes() -> dict:
    """Load and index the full nodes database by node name. Cached after first load."""
    global _nodes_cache
    if _nodes_cache is not None:
        return _nodes_cache
    
    with open(_NODES_FILE, "r", encoding="utf-8") as f:
        nodes_list = json.load(f)
    
    # Index by the 'name' field (e.g. 'n8n-nodes-base.slack')
    _nodes_cache = {}
    for node in nodes_list:
        node_name = node.get("name", "")
        if node_name and node_name not in _nodes_cache:
            _nodes_cache[node_name] = node
            
    return _nodes_cache


def _summarize_node(node: dict) -> dict:
    """Create a focused, lightweight summary of a node's schema for LLM consumption."""
    summary = {
        "displayName": node.get("displayName"),
        "name":        node.get("name"),
        "description": node.get("description"),
        "version":     node.get("defaultVersion") or node.get("version") or 1,
        "credentials": node.get("credentials", []),
        "properties":  []
    }
    
    for prop in node.get("properties", []):
        p = {
            "name":        prop.get("name"),
            "displayName": prop.get("displayName"),
            "type":        prop.get("type"),
            "required":    prop.get("required", False),
            "default":     prop.get("default"),
            "description": prop.get("description", ""),
        }
        
        # Include options if present, capped at 20 options
        if prop.get("options"):
            p["options"] = [
                {
                    "name":  o.get("name"),
                    "value": o.get("value"),
                    "description": o.get("description", "")
                }
                for o in prop["options"][:20]
            ]
            
        # Include displayOptions to show when this parameter is visible
        if prop.get("displayOptions"):
            p["displayOptions"] = prop["displayOptions"]
            
        summary["properties"].append(p)
        
    return summary


async def get_node_summary(node_name: str) -> dict:
    """
    Retrieve a lightweight parameter and credential summary for a specific n8n node type.
    Call this tool to get properties, credentials, and parameters for a node
    before using it in a workflow.

    Args:
        node_name: The technical or display name of the n8n node (e.g. 'n8n-nodes-base.slack', 
            'slack', 'Slack', 'postgres').

    Returns:
        A dictionary containing the node's parameters, credentials, and options.
    """
    try:
        nodes_db = _load_nodes()
    except FileNotFoundError:
        return {
            "status": "system_error",
            "error": "Node database file (nodes.json) not found. Run the node indexer first.",
            "instructions": "FATAL: Cannot proceed without node database."
        }
    except json.JSONDecodeError as e:
        return {
            "status": "system_error",
            "error": f"Node database is corrupted: {e}",
            "instructions": "FATAL: Cannot proceed. Report this error."
        }
    
    node_name_lower = node_name.lower().strip()
    
    # 1. Try exact match on technical name or suffix / display name
    matches = []
    for name, node in nodes_db.items():
        display_name = node.get("displayName", "")
        short_name = name.split(".")[-1]
        
        name_lower = name.lower()
        display_name_lower = display_name.lower()
        short_name_lower = short_name.lower()
        
        if (node_name_lower == name_lower or 
            node_name_lower == display_name_lower or 
            node_name_lower == short_name_lower):
            return {
                "status": "success",
                "node_summary": _summarize_node(node)
            }
            
        # 2. Try partial match fallback
        if (node_name_lower in name_lower or 
            node_name_lower in display_name_lower or 
            node_name_lower in short_name_lower):
            matches.append(node)
            
    # If exactly one partial match was found, return it
    if len(matches) == 1:
        return {
            "status": "success",
            "node_summary": _summarize_node(matches[0])
        }
        
    # If multiple matches found, return their info so the caller can specify
    if len(matches) > 1:
        return {
            "status": "not_found",
            "error": f"Multiple nodes matched '{node_name}'.",
            "similar_nodes": [
                {
                    "name": n.get("name"),
                    "displayName": n.get("displayName")
                }
                for n in matches[:10]
            ],
            "hint": "Please specify one of the technical names above."
        }
        
    return {
        "status": "not_found",
        "error": f"Node '{node_name}' not found and no similar nodes detected.",
        "hint": "Check the node_index to ensure the node name is correct."
    }


async def get_multiple_nodes_summary(node_names: list[str]) -> dict:
    """
    Retrieve lightweight parameter and credential summaries for multiple n8n node types in parallel.
    Call this tool to inspect multiple nodes at the same time to build/edit a workflow.

    Args:
        node_names: A list of node names (e.g. ['slack', 'postgres', 'gmail']).

    Returns:
        A dictionary mapping each node name to its parameter and credential summary, or a list of similar options if not found.
    """
    import asyncio
    
    tasks = [get_node_summary(name) for name in node_names]
    results = await asyncio.gather(*tasks)
    
    combined = {}
    for name, res in zip(node_names, results):
        combined[name] = res
        
    return {
        "status": "success",
        "node_summaries": combined
    }
