"""
HAITOMAS ASSISTANT — Content Ranker
Ranks scraped content by quality and relevance.
"""


class ContentRanker:
    """Ranks search results by quality and relevance."""

    # High-quality domain indicators
    QUALITY_DOMAINS = {
        "wikipedia.org": 9, "arxiv.org": 9, "github.com": 8,
        "stackoverflow.com": 8, "docs.python.org": 8, "mozilla.org": 8,
        "medium.com": 6, "dev.to": 7, "oreilly.com": 8,
        "geeksforgeeks.org": 6, "w3schools.com": 5,
    }

    def rank(self, results: list, query: str = "") -> list:
        """Rank results by quality metrics."""
        scored = []
        for r in results:
            score = self._calculate_score(r, query)
            r["quality_score"] = score
            scored.append(r)

        scored.sort(key=lambda x: x["quality_score"], reverse=True)
        return scored

    def _calculate_score(self, result: dict, query: str) -> float:
        """Calculate quality score for a single result."""
        score = 5.0  # Base score
        url = result.get("url", "")
        content = result.get("content", "") or result.get("snippet", "")
        title = result.get("title", "")

        # Domain quality
        for domain, bonus in self.QUALITY_DOMAINS.items():
            if domain in url:
                score = max(score, bonus)
                break

        # Content length bonus (more content = more useful)
        if len(content) > 1000:
            score += 1
        elif len(content) > 500:
            score += 0.5

        # Query relevance
        if query:
            q_words = query.lower().split()
            matches = sum(1 for w in q_words if w in title.lower() or w in content.lower())
            score += min(matches * 0.5, 2.0)

        return min(score, 10.0)
