try:
    import asyncio
    import aiohttp
    AIO_AVAILABLE = True
except ImportError:
    AIO_AVAILABLE = False

import trafilatura
from bs4 import BeautifulSoup
import requests

class ContentScraper:
    """High-performance scraper with synchronous fallback for maximum stability."""
    def __init__(self, concurrent_limit=10):
        self.limit = concurrent_limit

    async def fetch_and_extract(self, session, item):
        """Asynchronously fetch a URL and extract clean content."""
        url = item.get("url")
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    content = trafilatura.extract(html, include_comments=False, no_tables=True)
                    item["raw_content"] = content if content else ""
                    item["status"] = "success"
                else:
                    item["status"] = f"failed_{response.status}"
        except Exception as e:
            item["status"] = f"error_{str(e)}"
            item["raw_content"] = ""
        return item

    async def scrape_all(self, results):
        """Orchestrate scraping with dynamic library detection."""
        if AIO_AVAILABLE:
            try:
                async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
                    tasks = [self.fetch_and_extract(session, item) for item in results]
                    return await asyncio.gather(*tasks)
            except:
                pass # Fallback to sync
        
        # Synchronous Fallback (Reliable but slower)
        print("[Warning] aiohttp missing or failed. Using synchronous scraping fallback.")
        for item in results:
            try:
                downloaded = trafilatura.fetch_url(item.get("url"))
                content = trafilatura.extract(downloaded)
                item["raw_content"] = content if content else ""
                item["status"] = "success"
            except:
                item["raw_content"] = ""
        return results
