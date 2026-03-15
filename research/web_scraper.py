"""
HAITOMAS ASSISTANT — Web Scraper
High-precision web content extraction using Trafilatura and BeautifulSoup.
"""
import requests


class WebScraper:
    """Extract clean text content from web pages."""

    def scrape(self, url: str) -> dict:
        """Scrape a URL and extract clean content."""
        try:
            import trafilatura

            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return self._fallback_scrape(url)

            content = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )

            if content:
                return {
                    "url": url,
                    "content": content[:3000],
                    "method": "trafilatura",
                    "success": True
                }
            return self._fallback_scrape(url)

        except ImportError:
            return self._fallback_scrape(url)
        except Exception as e:
            return {"url": url, "content": "", "error": str(e), "success": False}

    def _fallback_scrape(self, url: str) -> dict:
        """Fallback scraping using BeautifulSoup."""
        try:
            from bs4 import BeautifulSoup

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "lxml")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            return {
                "url": url,
                "content": text[:3000],
                "method": "beautifulsoup",
                "success": True
            }
        except Exception as e:
            return {"url": url, "content": "", "error": str(e), "success": False}

    def scrape_multiple(self, urls: list) -> list:
        """Scrape multiple URLs."""
        return [self.scrape(url) for url in urls[:5]]
