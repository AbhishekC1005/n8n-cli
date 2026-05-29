import asyncio
from n8n_agent.client import n8n

async def test():
    print("Testing ping...")
    ok = await n8n.ping()
    print("Ping:", ok)
    try:
        workflows = await n8n.get_workflows()
        print("Workflows count:", len(workflows))
        for w in workflows[:3]:
            print(f"- {w.get('id')}: {w.get('name')}")
    except Exception as e:
        print("Error getting workflows:", e)
    finally:
        await n8n.close()

if __name__ == "__main__":
    asyncio.run(test())
