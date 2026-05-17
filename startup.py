import asyncio
from rich.console import Console
from rich.panel import Panel

from config import settings, ensure_agent_home
from n8n.client import client
from storage import init_db, get_memory, get_cached_nodes, save_nodes_cache
from storage.cache import is_cache_valid
from packages.cli.display import show_spinner, show_error, show_success

console = Console()


async def startup():
    ensure_agent_home()

    console.print(Panel("[bold]Initializing n8n-agent...[/bold]", border_style="blue"))

    async def check_n8n():
        with show_spinner("Checking n8n connection..."):
            healthy = await client.ping()
        if not healthy:
            show_error(f"n8n not found at {settings.N8N_BASE_URL}. Is it running?")
            return False
        return True

    async def load_nodes():
        if is_cache_valid():
            return True
        with show_spinner("Fetching node schemas..."):
            try:
                nodes = await client.get_installed_nodes()
                await save_nodes_cache(nodes)
                return True
            except Exception as e:
                show_error(f"Failed to load nodes: {e}")
                return False

    async def load_creds():
        with show_spinner("Loading credentials..."):
            try:
                creds = await client.get_credentials()
                return True
            except Exception:
                return False

    async def load_memory():
        get_memory()
        return True

    async def load_db():
        await init_db()
        return True

    results = await asyncio.gather(
        check_n8n(),
        load_nodes(),
        load_creds(),
        load_memory(),
        load_db(),
    )

    if not results[0]:
        raise SystemExit(1)

    console.print("[green]Ready.[/green]\n")
