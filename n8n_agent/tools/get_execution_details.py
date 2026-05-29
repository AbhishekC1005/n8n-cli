"""
get_execution_details tool for retrieving full runtime and error information for a specific n8n workflow execution.
"""

from n8n_agent.client import n8n, N8nAPIError


async def get_execution_details(execution_id: str) -> dict:
    """
    Retrieve full execution logs and errors for a specific workflow execution ID.
    Call this tool when a workflow run fails to find exactly which node failed, 
    what parameters it had, and what error message it returned.

    Args:
        execution_id: The unique ID of the specific execution run to investigate.

    Returns:
        A dictionary containing status, node execution states, error logs, and inputs/outputs.
    """
    try:
        details = await n8n.get_execution_details(execution_id)
        
        # Format a clean developer-friendly diagnostic summary if there is a failure
        status = details.get("status", "unknown")
        finished = details.get("finished", False)
        
        error_info = {}
        if not finished or status in ("failed", "crashed"):
            # Try to extract the error details
            error = details.get("data", {}).get("resultData", {}).get("error", {})
            if error:
                error_info = {
                    "nodeName": error.get("nodeName", "Unknown Node"),
                    "message": error.get("message", "No message"),
                    "description": error.get("description", "No description"),
                    "details": error.get("details", {})
                }
            else:
                # Fallback to scanning execution data for crashed nodes
                run_data = details.get("data", {}).get("resultData", {}).get("runData", {})
                for node_name, runs in run_data.items():
                    for run in runs:
                        if run.get("error"):
                            error_info = {
                                "nodeName": node_name,
                                "message": str(run["error"].get("message", "Error in execution")),
                                "description": str(run["error"].get("description", ""))
                            }
                            break
        
        response_data = {
            "status": "success",
            "execution_id": execution_id,
            "workflow_id": details.get("workflowId"),
            "run_status": status,
            "finished": finished,
            "started_at": details.get("startedAt"),
            "stopped_at": details.get("stoppedAt"),
        }
        
        if error_info:
            response_data["failure_diagnostics"] = error_info
            
        # We also include a list of nodes that executed successfully vs nodes that failed
        run_data = details.get("data", {}).get("resultData", {}).get("runData", {})
        executed_nodes = []
        for node_name, runs in run_data.items():
            for run in runs:
                executed_nodes.append({
                    "node": node_name,
                    "success": not bool(run.get("error")),
                    "execution_time": run.get("executionTime", 0)
                })
        response_data["executed_nodes"] = executed_nodes
        
        return response_data
        
    except N8nAPIError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"Failed to retrieve execution details: {e}"}
