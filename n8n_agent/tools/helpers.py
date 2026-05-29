"""
Shared validation helpers for n8n workflow tools.
"""

from typing import Optional


def validate_workflow_structure(wf_data: dict) -> Optional[str]:
    """Validate basic n8n workflow structure. Returns error string or None."""
    if not isinstance(wf_data, dict):
        return "Workflow must be a JSON object"

    if "name" not in wf_data:
        return "Workflow must have a 'name' field"

    nodes = wf_data.get("nodes")
    if not isinstance(nodes, list) or len(nodes) == 0:
        return "Workflow must have a non-empty 'nodes' array"

    node_names = set()
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            return f"Node at index {i} must be a JSON object"
        for required in ("name", "type", "position"):
            if required not in node:
                return f"Node '{node.get('name', f'index {i}')}' is missing required field '{required}'"
        pos = node.get("position")
        if isinstance(pos, dict) and ("x" not in pos or "y" not in pos):
            return f"Node '{node['name']}' position must have 'x' and 'y' fields"
        elif isinstance(pos, list) and len(pos) < 2:
            return f"Node '{node['name']}' position array must have at least 2 elements [x, y]"
        
        name = node["name"]
        if name in node_names:
            return f"Duplicate node name found: '{name}'. n8n node names must be unique."
        node_names.add(name)

    # Check for trigger node
    has_trigger = any(
        "Trigger" in node.get("type", "") or 
        "Webhook" in node.get("type", "") or 
        "Schedule" in node.get("type", "") or
        "Manual" in node.get("type", "") or
        node.get("type", "").endswith(".trigger")
        for node in nodes
    )
    if not has_trigger:
        return (
            "Workflow should have at least one trigger/starter node (type containing "
            "'Trigger', 'Webhook', 'Schedule', 'Manual', or ending with '.trigger')"
        )

    # Connection verification
    connections = wf_data.get("connections", {})
    if not isinstance(connections, dict):
        return "Workflow connections must be a JSON object"

    for source_name, connection_types in connections.items():
        if source_name not in node_names:
            return (
                f"Connection error: Connections map contains source node '{source_name}', "
                "which is not defined in the nodes list. Available nodes: "
                f"{list(node_names)}"
            )
        
        if not isinstance(connection_types, dict):
            return f"Connection connection types for '{source_name}' must be a JSON object"
            
        for conn_type, outputs in connection_types.items():
            if not isinstance(outputs, list):
                return f"Outputs list for connection type '{conn_type}' under '{source_name}' must be an array"
                
            for i, branch in enumerate(outputs):
                if not isinstance(branch, list):
                    return f"Branch {i} for connection type '{conn_type}' under '{source_name}' must be an array of connection targets"
                    
                for j, target in enumerate(branch):
                    if not isinstance(target, dict):
                        return f"Connection target at branch {i}, index {j} under '{source_name}' must be a JSON object"
                    if "node" not in target:
                        return f"Connection target at branch {i}, index {j} under '{source_name}' is missing target 'node' name"
                    
                    target_name = target["node"]
                    if target_name not in node_names:
                        return (
                            f"Connection error: Node '{source_name}' tries to connect to target node '{target_name}', "
                            "which does not exist in the nodes list. Available nodes: "
                            f"{list(node_names)}"
                        )

    return None

