import asyncio
from playwright.async_api import async_playwright
import os

class WebAutomation:
    """Advanced Browser Automation Layer (Layer 4).
    Uses Playwright for high-speed, headless or headed browser control.
    """
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def start(self, headless=False):
        """Initializes the playwright browser session."""
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        return "Browser Engine Online."

    async def navigate_and_extract(self, url):
        """Navigates to a URL and extracts human-readable text."""
        if not self.page: await self.start()
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            title = await self.page.title()
            # Intelligent content extraction (removing script/styles)
            content = await self.page.evaluate('''() => {
                const unwanted = ['script', 'style', 'nav', 'footer', 'header'];
                unwanted.forEach(tag => {
                    const elements = document.getElementsByTagName(tag);
                    while (elements[0]) elements[0].parentNode.removeChild(elements[0]);
                });
                return document.body.innerText;
            }''')
            return {"title": title, "content": content[:2000]}
        except Exception as e:
            return {"error": str(e)}

    async def smart_click(self, selector):
        """Attempts to click an element by text, id, or css."""
        if not self.page: return "Error: Browser not active."
        try:
            # Try finding by text first (human-like behavior)
            if not selector.startswith('.') and not selector.startswith('#'):
                await self.page.click(f"text='{selector}'", timeout=5000)
            else:
                await self.page.click(selector, timeout=5000)
            return f"Clicked: {selector}"
        except:
            return f"Failed to click: {selector}"

    async def smart_type(self, selector, text):
        """Types text into a field."""
        if not self.page: return "Error: Browser not active."
        try:
            await self.page.fill(selector, text)
            await self.page.keyboard.press("Enter")
            return f"Typed '{text}' into {selector}"
        except:
            return f"Failed to type into {selector}"

    async def close(self):
        """Cleans up resources."""
        if self.browser:
            await self.browser.close()
            await self.pw.stop()
            self.browser = None
        return "Browser Engine Offline."
