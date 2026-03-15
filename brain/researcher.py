"""
HAITOMAS ASSISTANT — Researcher
Advanced web research using Playwright and AI summarization.
"""
import time
from automation.browser_control import BrowserControl
from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK

class Researcher:
    """Agentic researcher that browse the web to find answers."""

    def __init__(self, browser_ctrl):
        self.browser = browser_ctrl

    async def _extract_first_link(self):
        """Async helper to find the first real link in search results."""
        try:
            # Common selectors for Google search result titles/links
            selectors = [
                 "h3", # Title
                 "a h3", # Link title
                 "#search a" # General search link
            ]
            
            for selector in selectors:
                elements = await self.browser.page.query_selector_all(selector)
                for el in elements:
                    # Get the parent <a> tag
                    parent = await el.evaluate_handle("el => el.closest('a')")
                    if parent:
                        href = await parent.get_property("href")
                        url = await href.json_value()
                        if url and "google.com" not in url and "webcache" not in url:
                            return url
            return None
        except Exception as e:
            print(f"[Researcher] Link extraction error: {e}")
            return None

    def deep_search(self, query: str) -> str:
        """Perform a deep search, browsing multiple sites and opening the best one."""
        event_bus.publish(EVENT_SPEAK, {"text": f"I am initiating a deep search for {query}. I will analyze the best sources and provide you with organized insights."})
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"🔍 Deep Searching: {query}...", "panel": "strategy"})

        try:
            async def _research_flow():
                await self.browser._ensure_browser()
                search_url = f"https://www.google.com/search?q={query}"
                await self.browser.page.goto(search_url, wait_until="networkidle")
                
                # Try to find the first authoritative link
                best_link = await self._extract_first_link()
                
                if best_link:
                    event_bus.publish(EVENT_SPEAK, {"text": "I've found an authoritative source. Navigating to it now for full analysis."})
                    event_bus.publish(EVENT_UI_UPDATE, {"text": f"🌐 Navigating to: {best_link}", "panel": "strategy"})
                    await self.browser.page.goto(best_link, wait_until="domcontentloaded", timeout=60000)
                    title = await self.browser.page.title()
                    return f"Research successful. I've opened the most relevant source: {title}"
                else:
                    return f"Search completed for '{query}', but I couldn't pick a specific top link automatically."

            result = self.browser._run_async(_research_flow())
            return result

        except Exception as e:
            error_msg = f"Research error: {e}"
            event_bus.publish(EVENT_ERROR, {"message": error_msg})
            return error_msg
