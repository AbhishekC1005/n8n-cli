from typing import Optional

from n8n.schemas import WorkflowData, WorkflowNode, NodePosition
from storage.cache import get_cached_nodes
from n8n.client import client


async def validate_workflow(workflow_json: dict) -> Optional[str]:
    try:
        workflow = WorkflowData(**workflow_json)
    except Exception as e:
        return f"Structural error: {str(e)}"

    node_types = await get_cached_nodes()
    if not node_types:
        try:
            node_types = await client.get_installed_nodes()
        except Exception:
            pass

    if node_types:
        installed_types = {n.name for n in node_types}
        for node in workflow.nodes:
            if node.type not in installed_types:
                return f"Unknown node type: '{node.type}' is not installed. Available: {', '.join(sorted(installed_types)[:20])}..."

    creds = await client.get_credentials()
    cred_ids = {c.id for c in creds}
    for node in workflow.nodes:
        if node.credentials:
            for cred_ref in node.credentials.values():
                if isinstance(cred_ref, dict) and "id" in cred_ref:
                    if cred_ref["id"] not in cred_ids:
                        return f"Invalid credential ID: '{cred_ref['id']}' not found in available credentials"

    positions = set()
    for node in workflow.nodes:
        pos = (node.position.x, node.position.y)
        if pos in positions:
            return f"Duplicate node position: {node.name} at ({node.position.x}, {node.position.y})"
        positions.add(pos)

    if workflow.connections:
        all_node_names = {n.name for n in workflow.nodes}
        for source_node, outputs in workflow.connections.items():
            if source_node not in all_node_names:
                return f"Connection references unknown node: '{source_node}'"
            for output_key, connections in outputs.items():
                for conn in connections:
                    for target in conn:
                        if target.get("node") not in all_node_names:
                            return f"Connection references unknown node: '{target.get('node')}'"

    has_trigger = any(
        "Trigger" in node.type or "Webhook" in node.type or "Schedule" in node.type
        for node in workflow.nodes
    )
    if not has_trigger:
        return "No trigger node found. Workflow must have at least one trigger (type contains 'Trigger', 'Webhook', or 'Schedule')"

    return None
