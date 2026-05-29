"""
get_templates tool for retrieving standard reference n8n JSON templates to guide workflow generation.
"""

import os
import json
from typing import Optional

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")


async def get_templates(template_name: Optional[str] = None) -> dict:
    """
    List available workflow reference templates, or retrieve the complete JSON skeleton of a specific template.
    Call this tool when you need standard n8n JSON structures, triggers, connection wiring, or node formatting.

    Args:
        template_name: The optional name of the specific template to retrieve (e.g. 'http_request', 'webhook_trigger', 'schedule_trigger').
            If not provided, returns a list of all available templates.

    Returns:
        A dictionary containing either a list of available templates or the parsed workflow JSON skeleton.
    """
    try:
        # Guarantee templates directory exists
        if not os.path.exists(TEMPLATES_DIR):
            return {"status": "error", "error": f"Templates directory does not exist at {TEMPLATES_DIR}"}

        files = [f for f in os.listdir(TEMPLATES_DIR) if f.endswith(".json")]

        # List mode
        if not template_name:
            template_list = []
            for file in files:
                name = os.path.splitext(file)[0]
                filepath = os.path.join(TEMPLATES_DIR, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    template_list.append({
                        "template_name": name,
                        "description": f"Reference skeleton for a {data.get('name', name)} workflow."
                    })
                except Exception:
                    template_list.append({
                        "template_name": name,
                        "description": "JSON reference skeleton"
                    })
            return {
                "status": "success",
                "available_templates": template_list,
                "message": "Call get_templates(template_name='...') to retrieve a specific skeleton structure."
            }

        # Specific template fetch mode
        # Normalize name
        template_name = template_name.replace(".json", "").lower().strip()
        match_file = None
        for file in files:
            if os.path.splitext(file)[0].lower() == template_name:
                match_file = file
                break

        if not match_file:
            return {
                "status": "error",
                "error": f"Template '{template_name}' not found. Available templates: {[os.path.splitext(f)[0] for f in files]}"
            }

        filepath = os.path.join(TEMPLATES_DIR, match_file)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "status": "success",
            "template_name": os.path.splitext(match_file)[0],
            "workflow_skeleton": data
        }

    except Exception as e:
        return {"status": "error", "error": f"Failed to retrieve templates: {e}"}
