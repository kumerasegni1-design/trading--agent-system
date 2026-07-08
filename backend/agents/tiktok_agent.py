import logging
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class TikTokAgent(BaseAgent):
    """
    Agent responsible for monitoring TikTok for trading strategies
    and extracting them for backtesting.
    """

    def __init__(self, event_bus):
        super().__init__(event_bus, "TikTokAgent")
        self.base_url = "https://www.tiktok.com/search?q="

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type")
        task_id = task.get("task_id")

        if task_type == "search_strategies":
            query = task.get("query", "trading strategy")
            result = await self.search_tiktok_strategies(query)
        else:
            result = {"status": "error", "message": f"Unknown task type: {task_type}"}

        await self.log_task(task_id, "completed", result)
        return result

    async def search_tiktok_strategies(self, query: str) -> Dict[str, Any]:
        """Scrape TikTok search results for trading strategies"""
        logger.info(f"📱 Searching TikTok for: {query}")

        search_url = f"{self.base_url}{query.replace(' ', '+')}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status != 200:
                        return {"status": "error", "message": f"TikTok returned status {response.status}"}

                    html = await response.text()
                    strategies = self._parse_tiktok_results(html)

                    return {
                        "status": "success",
                        "query": query,
                        "found_strategies": strategies
                    }
        except Exception as e:
            logger.error(f"❌ TikTok search failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _parse_tiktok_results(self, html: str) -> List[Dict]:
        """Parse HTML to find video descriptions and links"""
        soup = BeautifulSoup(html, 'html.parser')
        videos = []

        # This is a simplified selector, TikTok's classes change frequently
        # In a real scenario, we'd use a more robust way (e.g. Playwright or TikTok API)
        for container in soup.find_all('div', {'data-e2e': 'search_video-item'}):
            desc_elem = container.find('div', {'data-e2e': 'search_video-desc'})
            link_elem = container.find('a')

            if desc_elem and link_elem:
                videos.append({
                    "description": desc_elem.text,
                    "url": link_elem.get('href'),
                    "platform": "tiktok"
                })

        # If no results found with selectors, we might use regex or return empty
        if not videos:
            logger.warning("⚠️ No TikTok videos found with current selectors")

        return videos
