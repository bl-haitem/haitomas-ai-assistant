"""
HAITOMAS ASSISTANT — Browser Control
Advanced browser automation using Playwright.
"""
import asyncio
import threading


class BrowserControl:
    """Playwright-based browser automation for web tasks."""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self._lock = threading.Lock()

    def _run_async(self, coro):
        """Helper to run async code from sync context."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _ensure_browser(self):
        """Ensure browser is started."""
        if self.browser is None:
            from playwright.async_api import async_playwright
            self._pw = await async_playwright().start()
            self.browser = await self._pw.chromium.launch(headless=False)
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self.page = await self.context.new_page()

    def navigate(self, url: str) -> str:
        """Navigate to a URL and return page title."""
        try:
            async def _nav():
                await self._ensure_browser()
                if not url.startswith("http"):
                    full_url = f"https://{url}"
                else:
                    full_url = url
                await self.page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
                return await self.page.title()

            title = self._run_async(_nav())
            return f"Navigated to: {title}"
        except Exception as e:
            return f"Navigation error: {e}"

    def extract_content(self, url: str) -> dict:
        """Navigate and extract page content."""
        try:
            async def _extract():
                await self._ensure_browser()
                await self.page.goto(url, wait_until="networkidle", timeout=30000)
                title = await self.page.title()
                content = await self.page.evaluate("""() => {
                    const unwanted = ['script', 'style', 'nav', 'footer', 'header'];
                    unwanted.forEach(tag => {
                        const els = document.getElementsByTagName(tag);
                        while (els[0]) els[0].parentNode.removeChild(els[0]);
                    });
                    return document.body.innerText;
                }""")
                return {"title": title, "content": content[:2000]}

            return self._run_async(_extract())
        except Exception as e:
            return {"error": str(e)}

    def click_element(self, selector: str) -> str:
        """Click an element by text or CSS selector."""
        try:
            async def _click():
                await self._ensure_browser()
                if not selector.startswith(".") and not selector.startswith("#"):
                    await self.page.click(f"text='{selector}'", timeout=5000)
                else:
                    await self.page.click(selector, timeout=5000)
                return f"Clicked: {selector}"

            return self._run_async(_click())
        except Exception as e:
            return f"Click error: {e}"

    def type_in_field(self, selector: str, text: str) -> str:
        """Type text into a form field."""
        try:
            async def _type():
                await self._ensure_browser()
                await self.page.fill(selector, text)
                return f"Typed '{text}' into {selector}"

            return self._run_async(_type())
        except Exception as e:
            return f"Type error: {e}"

    def close(self) -> str:
        """Close the browser."""
        try:
            async def _close():
                if self.browser:
                    await self.browser.close()
                    await self._pw.stop()
                    self.browser = None
                    self.page = None

            self._run_async(_close())
            return "Browser closed."
        except Exception as e:
            return f"Close error: {e}"
