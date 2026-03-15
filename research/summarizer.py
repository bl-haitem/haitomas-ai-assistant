"""
HAITOMAS ASSISTANT — Summarizer
AI-powered content summarization using Gemini.
"""


class Summarizer:
    """Summarize content using the Gemini brain."""

    def __init__(self, gemini_controller):
        self.brain = gemini_controller

    def summarize(self, content: str, query: str = "") -> str:
        """Summarize content using Gemini."""
        prompt = f"Summarize the following content concisely and clearly"
        if query:
            prompt += f" in the context of '{query}'"
        prompt += f":\n\n{content[:3000]}"

        return self.brain.quick_ask(prompt)

    def create_report(self, query: str, results: list) -> str:
        """Create a structured research report from multiple sources."""
        combined = "\n\n".join([
            f"SOURCE: {r.get('title', 'Unknown')}\n"
            f"URL: {r.get('url', '')}\n"
            f"CONTENT: {r.get('content', r.get('snippet', ''))[:800]}"
            for r in results[:4]
        ])

        prompt = (
            f"Create a structured intelligence report for the query: '{query}'\n\n"
            f"Based on these sources:\n{combined}\n\n"
            f"Format: Executive summary, key findings, and conclusions."
        )

        return self.brain.quick_ask(prompt)
