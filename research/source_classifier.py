import re

class SourceClassifier:
    """Classifies sources into types using URL patterns and content analysis."""
    
    PATTERNS = {
        "video": [r"youtube\.com", r"vimeo\.com", r"coursera\.org/lecture", r"ted\.com"],
        "course": [r"udemy\.com", r"coursera\.org", r"edx\.org", r"ocw\.mit\.edu", r"khanacademy\.org"],
        "documentation": [r"docs\.", r"readthedocs\.io", r"developers\.", r"wiki", r"developer\."],
        "tutorial": [r"tutorialspoint", r"geeksforgeeks", r"freecodecamp", r"medium\.com/.*tutorial"],
        "article": [r"blog\.", r"medium\.com", r"nytimes\.com", r"theverge\.com"]
    }

    def classify(self, item):
        url = item.get("url", "").lower()
        title = item.get("title", "").lower()
        
        for kind, patterns in self.PATTERNS.items():
            if any(re.search(p, url) for p in patterns):
                return kind
        
        # Fallback using title keywords
        if "video" in title: return "video"
        if "course" in title: return "course"
        if "documentation" in title or "manual" in title: return "documentation"
        
        return "article"
