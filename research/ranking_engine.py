class RankingEngine:
    """Ranks results based on AI scores, domain weight, and content density."""
    
    DOMAIN_WEIGHTS = {
        "edu": 2.0,
        "gov": 1.5,
        "org": 1.2,
        "mits": 2.5, # Special weight for MIT, etc.
        "youtube": 1.1 
    }

    def rank(self, results):
        """Sort results by a weighted quality score."""
        for item in results:
            base_score = item.get("ai_score", 5.0)
            
            # Domain Booster
            domain_bonus = 1.0
            url = item.get("url", "").lower()
            if ".edu" in url: domain_bonus = self.DOMAIN_WEIGHTS["edu"]
            elif ".gov" in url: domain_bonus = self.DOMAIN_WEIGHTS["gov"]
            elif "mit.edu" in url or "stanford.edu" in url: domain_bonus = self.DOMAIN_WEIGHTS["mits"]
            
            # Content Length Booster (penalize thin content)
            length = len(item.get("raw_content", ""))
            length_multiplier = 1.0
            if length < 500: length_multiplier = 0.5
            elif length > 3000: length_multiplier = 1.2
            
            item["final_score"] = round(base_score * domain_bonus * length_multiplier, 2)
            
        # Global Sort
        return sorted(results, key=lambda x: x["final_score"], reverse=True)
