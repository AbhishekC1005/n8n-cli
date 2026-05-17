from n8n.schemas import NodeInfo


def parse_node_schema(node: NodeInfo) -> dict:
    return {
        "name": node.name,
        "displayName": node.displayName,
        "description": node.description,
        "version": node.version,
        "credentials": node.credentials or [],
    }


def format_node_list(nodes: list[NodeInfo]) -> str:
    lines = []
    for node in nodes:
        lines.append(f"- {node.name}: {node.displayName} ({node.version})")
        if node.description:
            lines.append(f"  {node.description[:100]}")
    return "\n".join(lines)
