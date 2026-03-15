class ContentAnalyzer:
    """Uses the local Brain to evaluate and score research content."""
    def __init__(self, brain):
        self.brain = brain

    def analyze(self, query, item):
        """Analyze a single item and return a quality score and explanation."""
        content_preview = item.get("raw_content", "")[:1500] # Give the LLM a good chunk
        if not content_preview:
            return 0.1, "No content extracted."

        prompt = f"""
        Analyze this web content for its educational value regarding the query: "{query}"
        
        [CONTENT START]
        {content_preview}
        [CONTENT END]

        [INSTRUCTION]
        Provide a quality score from 1.0 to 10.0 and a brief explanation (1 sentence).
        Format: SCORE: [value] | WHY: [explanation]
        """
        
        result = self.brain.quick_ask(prompt)
        if not result: return 0.5, "Analysis failed."

        try:
            # Parse the LLM response
            score_part = result.split("|")[0].replace("SCORE:", "").strip()
            score = float(score_part)
            explanation = result.split("|")[1].replace("WHY:", "").strip()
            return score, explanation
        except:
            return 5.0, "Analysis completed with ambiguous scoring."
