"""
HAITOMAS ASSISTANT — Web Search
DuckDuckGo-based web search engine.
"""


class WebSearch:
    """Search the web using DuckDuckGo."""

    def search(self, query: str, max_results: int = 5) -> list:
        """Search and return list of results."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return [{
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                } for r in results]
        except Exception as e:
            print(f"[WebSearch] Error: {e}")
            return []

    def quick_answer(self, query: str) -> str:
        """Get a quick answer string from search results."""
        results = self.search(query, max_results=3)
        if not results:
            return "No search results found."
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"[{i}] {r['title']}\n    {r['snippet']}\n    {r['url']}")
        return "\n\n".join(parts)
