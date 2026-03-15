import asyncio
import re
import requests
from research.search_engine import SearchEngine
from research.content_scraper import ContentScraper
from research.content_analyzer import ContentAnalyzer
from research.source_classifier import SourceClassifier
from research.ranking_engine import RankingEngine

class ResearchAgent:
    """The 'Brain' of the Deep Research System. Orchestrates multi-stage intelligence gathering."""
    def __init__(self, brain):
        self.searcher = SearchEngine()
        self.scraper = ContentScraper()
        self.analyzer = ContentAnalyzer(brain)
        self.classifier = SourceClassifier()
        self.ranker = RankingEngine()
        self.brain = brain

    def quick_search(self, query: str) -> str:
        """Fast information retrieval using snippets only."""
        from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"🛰️ Fetching quick data: {query}", "panel": "strategy"})
        
        try:
            # Special logic for Weather - Force high reliability
            if "weather" in query.lower() or "طقس" in query:
                return self._fetch_weather_special(query)

            results = self.searcher.search(query)
            if not results:
                return "No instant results found."
            
            # Use top 5 snippets
            context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in results[:5]])
            lang = "ar" if any(ord(c) > 128 for c in query) else "en"
            prompt = f"Based on these search snippets, give a direct, concise answer to '{query}' in {lang}. Focus on facts:\n\n{context}"
            if lang == "ar":
                prompt = f"بناءً على نتائج البحث هذه، أعطِ إجابة مباشرة ومختصرة لـ '{query}' باللغة العربية. ركّز على الحقائق:\n\n{context}"
            
            answer = self.brain.quick_ask(prompt)
            
            if "Intelligence system overloaded" in answer or "Unable to synthesize" in answer:
                # Fallback: Just return a structured list of top results if AI fails to summarize
                event_bus.publish(EVENT_SPEAK, {"text": "I was unable to summarize the data, but here are the top findings."})
                fallback = f"Findings for {query}:\n" + "\n".join([f"- {r['title']}" for r in results[:3]])
                return fallback

            event_bus.publish(EVENT_SPEAK, {"text": answer})
            return answer
        except Exception as e:
            return f"Fetch error: {e}"

    def _fetch_weather_special(self, query: str) -> str:
        """Dedicated high-reliability weather extraction using multiple providers."""
        from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK
        event_bus.publish(EVENT_UI_UPDATE, {"text": "☁️ Accessing real-time meteorological data...", "panel": "strategy"})
        
        # Extract city from query
        city = "Jijel"
        # Match both English and Arabic city names
        city_match = re.search(r"(?:in|at|for|في|بمدينة|بـ)\s+([a-zA-Z\u0600-\u06FF\s]+)", query)
        if city_match:
            city = city_match.group(1).strip()

        # Vector 1: wttr.in (Best for quick stats)
        try:
            print(f"[Research] Attempting wttr.in for {city}...")
            wttr_url = f"https://wttr.in/{city}?format=%C+%t+%w+%h"
            resp = requests.get(wttr_url, timeout=10)
            if resp.status_code == 200 and len(resp.text) < 150:
                data = resp.text.strip()
                print(f"[Research] wttr.in raw: {data}")
                lang = "ar" if any(ord(c) > 128 for c in query) else "en"
                
                # Use AI to format the raw data nicely
                format_prompt = f"Convert this raw weather data into a friendly, professional update in {lang} for the location {city}: {data}. Mention temperature and sky."
                if lang == "ar":
                    format_prompt = f"حول بيانات الطقس الخام هذه إلى تحديث احترافي وودود باللغة العربية لمدينة {city}: {data}. اذكر درجة الحرارة والحالة العامة للسماء."
                
                answer = self.brain.quick_ask(format_prompt)
                if answer and "Intelligence system overloaded" not in answer:
                    event_bus.publish(EVENT_SPEAK, {"text": answer})
                    return answer
                else:
                    # Raw fallback if AI summary fails
                    fallback = f"Weather in {city}: {data}"
                    event_bus.publish(EVENT_SPEAK, {"text": fallback})
                    return fallback
        except Exception as e:
            print(f"[Research] wttr.in error: {e}")
            
        # Vector 2: Google Snippet Mining
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"🛰️ Scanning secondary weather satellites for {city}...", "panel": "strategy"})
        results = self.searcher.search(f"current weather and temperature in {city}")
        if results:
            context = "\n".join([f"- {r['snippet']}" for r in results[:5]])
            lang = "ar" if any(ord(c) > 128 for c in query) else "en"
            prompt = f"Based on these results, what is the EXACT current weather (Temp, Sky) in {city}? Answer in {lang}:\n\n{context}"
            answer = self.brain.quick_ask(prompt)
            if answer and "Intelligence system overloaded" not in answer:
                event_bus.publish(EVENT_SPEAK, {"text": answer})
                return answer

        return f"I'm having trouble reaching the weather stations for {city} at the moment, Commander. Please check the dashboard for manual links."

    def deep_search(self, query: str) -> str:
        """Synchronous wrapper for internal async research pipeline."""
        from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK
        from core.voice_library import get_phrase
        
        lang = "ar" if any(ord(c) > 128 for c in query) else "en"
        event_bus.publish(EVENT_SPEAK, {"text": get_phrase("research_start", lang)})
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"🔍 Researching: {query}", "panel": "strategy"})

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.run_deep_research(query))
            loop.close()
            
            # Post-success summary speak
            event_bus.publish(EVENT_SPEAK, {"text": "I have completed the deep intelligence synthesis. You can view the report in the dashboard."})
            return result
        except Exception as e:
            print(f"[ResearchAgent] Error: {e}")
            return f"Research failed: {e}"

    async def run_deep_research(self, query):
        """Execute the full Architect-level research pipeline."""
        from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK
        from core.voice_library import get_phrase
        lang = "ar" if any(ord(c) > 128 for c in query) else "en"

        print(f"[ResearchAgent] Initiating complex knowledge synthesis for: {query}")
        
        # 1. Multi-Vector Search
        event_bus.publish(EVENT_UI_UPDATE, {"text": "🛰️ Expanding intelligence vectors...", "panel": "strategy"})
        raw_results = self.searcher.search(query)
        if not raw_results:
            return "Intelligence Error: Knowledge pool empty."

        # 2. High-Speed Parallel Scraping
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"📥 Scraping {len(raw_results)} sources...", "panel": "strategy"})
        event_bus.publish(EVENT_SPEAK, {"text": get_phrase("searching_resources", lang)})
        scraped_results = await self.scraper.scrape_all(raw_results)
        
        # 3. Intelligent Classification
        event_bus.publish(EVENT_UI_UPDATE, {"text": "🧠 Classifying and ranking intelligence...", "panel": "strategy"})
        valid_results = [r for r in scraped_results if r.get("raw_content") and len(r["raw_content"]) > 400]
        for item in valid_results:
            item["type"] = self.classifier.classify(item)

        # 4. Deep Brain Analysis
        event_bus.publish(EVENT_UI_UPDATE, {"text": "🔬 Performing deep semantic analysis...", "panel": "strategy"})
        candidates = valid_results[:15]
        for item in candidates:
            score, why = self.analyzer.analyze(query, item)
            item["ai_score"] = score
            item["explanation"] = why

        # 5. Semantic Ranking System
        final_ranked = self.ranker.rank(candidates)
        top_results = final_ranked[:8]

        # 6. KNOWLEDGE SYNTHESIS
        event_bus.publish(EVENT_UI_UPDATE, {"text": "📝 Synthesizing executive report...", "panel": "strategy"})
        event_bus.publish(EVENT_SPEAK, {"text": get_phrase("waiting", lang)})
        combined_text = "\n\n".join([f"SOURCE: {r['title']}\nCONTENT: {r['raw_content'][:1000]}" for r in top_results[:4]])
        executive_summary = self.brain.quick_ask(f"Synthesize this raw data into a master explanation for '{query}'. Be profound, structured, and insightful:\n\n{combined_text}")

        # 7. Presentation Layer (Architect Style)
        report = []
        report.append(f"╔══════════════════════════════════════════════════════╗")
        report.append(f"║ HAITOMAS EXECUTIVE INTELLIGENCE REPORT               ║")
        report.append(f"╚══════════════════════════════════════════════════════╝\n")
        report.append(f"■ OBJECTIVE: Deep research on {query.upper()}\n")
        report.append(f"■ EXECUTIVE SUMMARY:\n{executive_summary}\n")
        report.append(f"■ TOP RECOMMENDED RESOURCES:\n")
        
        for i, res in enumerate(top_results):
            stars = "★" * int(res['final_score'] / 2) + "☆" * (5 - int(res['final_score'] / 2))
            report.append(f"[{i+1}] {res['title'].upper()}")
            report.append(f"    ├─ TYPE: {res['type'].upper()} | {stars} ({res['final_score']}/10)")
            report.append(f"    ├─ INSIGHT: {res.get('explanation')}")
            report.append(f"    └─ URL: {res['url']}\n")
            
        return "\n".join(report)
