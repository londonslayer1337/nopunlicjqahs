import asyncio
from holehe import holehe

async def search_email(email: str) -> dict:
    """Асинхронный поиск по email через Holehe."""
    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(
            None,
            lambda: holehe(email, only_used=True)
        )
        return {"found": results, "count": len(results) if results else 0}
    except Exception as e:
        return {"error": str(e)}
