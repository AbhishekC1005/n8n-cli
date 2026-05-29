"""
web_search tool for searching n8n documentation on DuckDuckGo.
"""


async def web_search(query: str) -> dict:
    """
    Search the web for n8n documentation, API usage examples, or troubleshooting.
    Use this when you need information about n8n node parameters, third-party APIs,
    or how to configure specific integrations.

    Args:
        query: The search query string.

    Returns:
        A dictionary with search results or a search URL.
    """
    import httpx as _httpx

    search_query = query.replace(" ", "+")
    search_url = f"https://duckduckgo.com/html/?q={search_query}+n8n"
    try:
        async with _httpx.AsyncClient() as http:
            resp = await http.get(
                search_url,
                timeout=10.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; n8nAgent/1.0)"},
            )
            if resp.status_code == 200:
                return {
                    "status": "success",
                    "query": query,
                    "message": f"Search results available at: {search_url}",
                    "hint": "Based on common n8n documentation patterns, try using the node type and parameters described in the official n8n docs.",
                }
            return {"status": "error", "error": f"Search returned status {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "error": f"Search failed: {e}"}
