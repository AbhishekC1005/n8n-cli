import json
import sys
import os

# ── CONFIG ───────────────────────────────────────────────────────────────────
NODE_TYPES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nodes.json")
# ─────────────────────────────────────────────────────────────────────────────

# load once at startup
with open(NODE_TYPES_FILE, "r", encoding="utf-8") as f:
    ALL_NODES = json.load(f)


def get_node_schema(node_name: str) -> dict:
    """
    Filter node_types.json and return schema for a specific node.
    node_name: e.g. 'slack', 'postgres', 'httpRequest', 'gmail'
    """
    node_name_lower = node_name.lower().strip()

    matches = []

    for node in ALL_NODES:
        name         = node.get("name", "")          # e.g. n8n-nodes-base.slack
        display_name = node.get("displayName", "")   # e.g. Slack
        short_name   = name.split(".")[-1]            # e.g. slack

        name_lower         = name.lower()
        display_name_lower = display_name.lower()
        short_name_lower   = short_name.lower()

        # exact match first
        if (node_name_lower == short_name_lower or
            node_name_lower == display_name_lower or
            node_name_lower == name_lower):
            return node  # exact match, return immediately

        # partial match fallback
        if (node_name_lower in short_name_lower or
            node_name_lower in display_name_lower):
            matches.append(node)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        # return list of matched names so user can be more specific
        return {
            "multiple_matches": [
                {
                    "name": n.get("name"),
                    "displayName": n.get("displayName")
                }
                for n in matches
            ],
            "hint": f"Be more specific. Found {len(matches)} matches for '{node_name}'"
        }

    return {"error": f"Node '{node_name}' not found in node_types.json"}


def get_node_summary(node_name: str) -> dict:
    """
    Returns a lightweight summary instead of the full schema.
    Useful for quick lookups without overwhelming the LLM.
    """
    schema = get_node_schema(node_name)

    if "error" in schema or "multiple_matches" in schema:
        return schema

    # extract only what matters for LLM context
    summary = {
        "displayName": schema.get("displayName"),
        "name":        schema.get("name"),
        "description": schema.get("description"),
        "version":     schema.get("defaultVersion") or schema.get("version"),
        "credentials": schema.get("credentials", []),
        "properties":  []
    }

    for prop in schema.get("properties", []):
        p = {
            "name":        prop.get("name"),
            "displayName": prop.get("displayName"),
            "type":        prop.get("type"),
            "required":    prop.get("required", False),
            "default":     prop.get("default"),
            "description": prop.get("description", ""),
        }

        # include options if present
        if prop.get("options"):
            p["options"] = [
                {
                    "name":  o.get("name"),
                    "value": o.get("value"),
                    "description": o.get("description", "")
                }
                for o in prop["options"][:20]  # cap at 20 options
            ]

        # include displayOptions so LLM knows when this param is visible
        if prop.get("displayOptions"):
            p["displayOptions"] = prop["displayOptions"]

        summary["properties"].append(p)

    return summary


def list_all_nodes() -> list:
    """
    Returns a flat list of all available nodes.
    Useful for LLM to know what nodes exist.
    """
    return [
        {
            "name":        node.get("name"),
            "displayName": node.get("displayName"),
            "description": node.get("description", ""),
            "group":       node.get("group", []),
        }
        for node in ALL_NODES
    ]


def search_nodes(keyword: str) -> list:
    """
    Search nodes by keyword across name, displayName, description.
    Returns matching nodes list.
    """
    keyword_lower = keyword.lower().strip()
    results = []

    for node in ALL_NODES:
        name        = node.get("name", "").lower()
        display     = node.get("displayName", "").lower()
        description = node.get("description", "").lower()

        if (keyword_lower in name or
            keyword_lower in display or
            keyword_lower in description):
            results.append({
                "name":        node.get("name"),
                "displayName": node.get("displayName"),
                "description": node.get("description", ""),
            })

    return results


# ── CLI USAGE ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python get_node_schema.py schema <node_name>     # full schema")
        print("  python get_node_schema.py summary <node_name>    # clean summary for LLM")
        print("  python get_node_schema.py search <keyword>       # search nodes")
        print("  python get_node_schema.py list                   # list all nodes")
        print()
        print("Examples:")
        print("  python get_node_schema.py schema slack")
        print("  python get_node_schema.py summary postgres")
        print("  python get_node_schema.py search email")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "schema" and len(sys.argv) >= 3:
        result = get_node_schema(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "summary" and len(sys.argv) >= 3:
        result = get_node_summary(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "search" and len(sys.argv) >= 3:
        result = search_nodes(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "list":
        result = list_all_nodes()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)