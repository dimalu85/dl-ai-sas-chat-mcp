# news_server.py — MCP Server for HackerNews (no API key required)
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("news")
HN_BASE = "https://hacker-news.firebaseio.com/v0"

@mcp.tool()
async def get_top_news(count: int = 10) -> str:
    """Get the top N stories from Hacker News (free, no API key)."""
    count = min(max(count, 1), 30)  # clamp 1-30
    async with httpx.AsyncClient() as client:
        # 1. Fetch top story IDs
        resp = await client.get(f"{HN_BASE}/topstories.json")
        resp.raise_for_status()
        ids = resp.json()[:count]

        # 2. Fetch each story in parallel
        tasks = [client.get(f"{HN_BASE}/item/{story_id}.json") for story_id in ids]
        responses = await asyncio.gather(*tasks)

    stories = []
    for i, r in enumerate(responses, 1):
        item = r.json()
        url = item.get("url")
        if not url:
            continue  # skip Ask HN / Show HN / jobs (no external link)
        title = item.get("title", "No title")
        score = item.get("score", 0)
        stories.append(f"{i}. [{score}pts] {title}\n   {url}")

    return "Top Hacker News stories:\n\n" + "\n\n".join(stories)

if __name__ == "__main__":
    mcp.run()
