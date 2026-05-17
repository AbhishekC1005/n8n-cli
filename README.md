# n8n Workflow Agent

AI-powered CLI agent that creates, edits, and manages [n8n](https://n8n.io) automation workflows using natural language. Built on **Google ADK** with **NVIDIA NIM** models via LiteLLM.

## Features

- **Natural language workflow creation** — describe what you want, the agent builds the n8n workflow JSON
- **Full n8n API integration** — list, view, create, update, activate, delete workflows
- **Credential awareness** — automatically fetches your saved n8n credentials
- **Execution debugging** — view recent execution history and errors
- **Interactive CLI** with Rich-powered formatting

## Quick Start

### Prerequisites

- Python 3.13+
- [n8n](https://n8n.io) running locally (default: `http://localhost:5678`)
- [NVIDIA NIM API key](https://build.nvidia.com/) (free tier available)

### Installation

```bash
git clone https://github.com/your-username/n8n-agent.git
cd n8n-agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
copy .env.example .env            # Windows
# cp .env.example .env            # macOS/Linux
```

Edit `.env` with your keys:

```env
NIM_API_KEY=nvapi-your-key-here
NVIDIA_NIM_API_KEY=nvapi-your-key-here
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL=openai/deepseek-ai/deepseek-v4-flash

N8N_API_KEY=your-n8n-api-key
N8N_BASE_URL=http://localhost:5678
```

> **Getting your n8n API key:** Open n8n → Settings → API → Generate API Key

### Usage

```bash
# Interactive chat mode
python main.py

# One-shot mode
python main.py "list all my workflows"
```

## Example Prompts

```
> list my workflows
> create a workflow that sends a Slack message every morning at 9am
> show me the details of my "Email Automation" workflow
> activate workflow 1R79s3KvMOTyTrHm
```

## Available NVIDIA NIM Models

The agent works with any chat model on NVIDIA NIM. Tested models:

| Model | Speed | Notes |
|-------|-------|-------|
| `openai/deepseek-ai/deepseek-v4-flash` | ~1.4s | **Recommended** — fast, good tool calling |
| `openai/meta/llama-3.3-70b-instruct` | ~1.4s | Good general purpose |
| `openai/meta/llama-3.1-8b-instruct` | ~0.3s | Fastest, lighter reasoning |
| `openai/nvidia/nemotron-3-super-120b-a12b` | ~5s | Largest, strongest reasoning |

Set via the `MODEL` env var in `.env`.

## Project Structure

```
n8n-agent/
├── main.py                    # Entry point (interactive + one-shot CLI)
├── adk_test/
│   ├── agent.py               # ADK agent definition + system prompt
│   └── tools/
│       ├── n8n_tools.py       # Tool functions exposed to the agent
│       └── n8n_client.py      # Async n8n REST API client
├── core/                      # Agent utilities
├── n8n/                       # n8n schemas
├── storage/                   # Persistence (cache, memory, backups)
├── config.py                  # Settings
├── .env.example               # Template environment config
├── requirements.txt           # Python dependencies
└── pyproject.toml             # Project metadata
```

## Architecture

```
User Input → Google ADK LlmAgent → LiteLLM → NVIDIA NIM API
                  ↕
           Tool Functions → n8n REST API (localhost:5678)
```

The agent uses Google ADK's `LlmAgent` with function-calling tools. When the user asks to create a workflow, the agent:

1. Fetches available credentials from n8n
2. Generates valid n8n workflow JSON
3. Creates/updates the workflow via the n8n REST API

## License

MIT