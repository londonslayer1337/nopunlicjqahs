import asyncio
from maigret import maigret

async def search_username(username: str, max_sites: int = 50) -> dict:
    """Асинхронный поиск по юзернейму через Maigret."""
    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(
            None,
            lambda: maigret(username, max_sites=max_sites, timeout=10, verbose=False)
        )
        found = []
        if results and "sites" in results:
            for site, data in results["sites"].items():
                if data.get("status") == "claimed":
                    found.append({"site": site, "url": data.get("url", "")})
        return {"found": found, "count": len(found)}
    except Exception as e:
        return {"error": str(e)}
