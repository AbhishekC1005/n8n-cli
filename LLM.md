# n8n Workflow Agent — Developer & LLM Wiki

This is the developer-facing Markdown version of the LLM wiki for the **n8n Workflow Agent** project. It outlines the codebase layout, components, and integration parameters to guide both AI systems and human developers in extending or maintaining the application.

> [!TIP]
> The raw text version of this document is maintained at `llms.txt` in the root of the project for direct LLM ingestion.

---

## 1. Directory Tree & Architecture

The codebase consists of a highly optimized and self-contained structure implementing the Google ADK path:

```
n8n-cli/
├── main.py                     # Entry point for Google ADK Agent (interactive & single-shot)
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Dependencies managed by uv (includes google-adk & litellm)
│
└── n8n_agent/                  # Google ADK Agent Code
    ├── agent.py                # Agent configuration & system instructions
    ├── client.py               # Lightweight async client mapping n8n REST API calls
    └── tools/                  # ADK Tool Set Modular Package
        ├── __init__.py         # Tools exporter package
        ├── helpers.py          # Validation rules
        ├── memory_store.py     # Share memory database dictionary
        ├── get_credentials.py
        ├── list_workflows.py
        ├── get_workflow.py
        ├── get_executions.py
        ├── create_workflow.py
        ├── update_workflow.py
        ├── activate_workflow.py
        ├── delete_workflow.py
        ├── save_memory.py
        ├── get_memory.py
        └── web_search.py
```

### The Agent Architecture
The application runs on a clean, single-path Google ADK architecture:
* **Google ADK Agent (`main.py` + `n8n_agent/`):** Instantiates Google ADK's `LlmAgent` using Python function definitions from the `n8n_agent/tools/` subpackage. It calls LiteLLM under the hood to invoke models hosted on NVIDIA NIM (such as `openai/deepseek-ai/deepseek-v4-flash` or `openai/meta/llama-3.3-70b-instruct`).

---

## 2. API Integration & n8n Tools

The agent interacts with n8n using a self-contained, lightweight async client (`adk_test/tools/n8n_client.py`) wrapping the n8n REST API. The client offers:
- **`ping()`**: Validates connectivity to `N8N_BASE_URL` with the defined API key.
- **`get_workflows()` / `get_workflow(id)`**: Fetches metadata list or complete JSON schemas of workflows.
- **`create_workflow(data)` / `update_workflow(id, data)`**: Creates or edits workflows with structural validation.
- **`activate_workflow(id)` / `deactivate_workflow(id)`**: Toggles workflow active status.
- **`delete_workflow(id)`**: Destroys workflow.
- **`get_credentials()`**: Queries active integrations (e.g., Slack, GitHub) to obtain credential IDs for node parameters.

---

## 3. Workflow Construction Rules for AIs

If you are an LLM generating workflow JSON schemas for this agent:

1. **Include Trigger Node:** Every valid n8n workflow must have a trigger node (e.g. `n8n-nodes-base.webhook` or `n8n-nodes-base.cron`) positioned at `[250, 300]`.
2. **Horizontal Layout:** Increment subsequent nodes horizontally by `250px` (e.g., `[500, 300]`, `[750, 300]`) to ensure the workflow is clean and readable inside the n8n UI.
3. **Credentials:** Query `get_credentials` before generating node structures. If matching credentials exist, reference them inside the node parameters:
   ```json
   "credentials": {
     "credentialType": {
       "id": "cred-uuid-or-id",
       "name": "My Slack Account"
     }
   }
   ```
4. **Safety & Destructive Actions:** Always prompt for confirmation before deleting or overwriting any workflow.
