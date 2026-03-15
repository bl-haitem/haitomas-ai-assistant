from ddgs import DDGS
import logging
import time

class SearchEngine:
    """Advanced Search Engine module for Haitomas Research System."""
    def __init__(self, max_results=30):
        self.max_results = max_results
        self.ddgs = DDGS()

    def search(self, query):
        """Advanced Multi-Stage Search with Query Expansion."""
        print(f"[Research] Expanding intelligence vectors for: {query}")
        
        # Query Expansion (AI-style logic)
        vectors = [
            query,
            f"comprehensive guide to {query}",
            f"{query} for beginners and experts",
            f"best university lectures on {query}",
            f"{query} technical documentation and tutorials",
            f"latest research papers on {query}"
        ]
        
        results_map = {}
        try:
            with DDGS() as ddgs:
                for v in vectors:
                    try:
                        print(f"  > Sweep Vector: {v}")
                        search_results = list(ddgs.text(v, max_results=8))
                        for r in search_results:
                            url = r.get("href")
                            if url and url not in results_map:
                                results_map[url] = {
                                    "title": r.get("title"),
                                    "url": url,
                                    "snippet": r.get("body"),
                                    "vector": v
                                }
                            if len(results_map) >= 40: break
                        if len(results_map) >= 40: break
                        time.sleep(0.5) # Avoid rate limits
                    except Exception:
                        continue
                        
        except Exception as e:
            logging.error(f"Deep Search Error: {e}")
            
        return list(results_map.values())
