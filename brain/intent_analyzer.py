"""
HAITOMAS ASSISTANT — Intent Analyzer
Ultra-fast local intent classification using keyword matching.
Handles instant responses without needing Gemini (greetings, identity, etc.)
"""
import re


class IntentAnalyzer:
    """Zero-latency intent detector for common patterns."""

    # Instant response patterns (no Gemini needed)
    INSTANT_PATTERNS = {
        "greeting": {
            "triggers": ["hi", "hello", "hey", "haitomas", "marhaba", "مرحبا", "سلام", "bonjour"],
            "response": {"type": "conversation", "reply": "HAITOMAS online. All systems nominal. How can I assist you, Commander?"}
        },
        "identity": {
            "triggers": ["who are you", "what are you", "your name", "identify yourself", "من انت", "ما اسمك"],
            "response": {"type": "conversation", "reply": "I am HAITOMAS — your advanced AI system operator. I control your computer with human-like intelligence and precision."}
        },
        "status": {
            "triggers": ["how are you", "how r u", "are you okay", "are you alive", "كيف حالك"],
            "response": {"type": "conversation", "reply": "All my neural systems are operating at peak capacity. Ready for any mission, Commander."}
        }
    }

    def analyze(self, text: str) -> dict | None:
        """
        Attempt to classify intent instantly without calling Gemini.
        Returns a structured response dict if matched, None otherwise.
        """
        t = text.lower().strip()

        # 1. Exact greeting match
        if t in ["hi", "hello", "hey", "haitomas", "مرحبا", "سلام"]:
            return self.INSTANT_PATTERNS["greeting"]["response"]

        # 2. Pattern matching
        for intent_name, data in self.INSTANT_PATTERNS.items():
            if any(trigger in t for trigger in data["triggers"]):
                return data["response"]

        # 3. Quick command detection (bypass Gemini for obvious commands)
        quick = self._quick_command_detect(t, text)
        if quick:
            return quick

        # No instant match — needs Gemini
        return None

    def _quick_command_detect(self, t: str, original: str) -> dict | None:
        """Detect obvious commands that don't need AI reasoning."""

        # Open application
        if t.startswith("open "):
            target = t.replace("open ", "").strip()

            # Website detection
            web_map = {
                "youtube": "https://www.youtube.com",
                "google": "https://www.google.com",
                "gmail": "https://mail.google.com",
                "facebook": "https://www.facebook.com",
                "chatgpt": "https://chat.openai.com",
                "github": "https://www.github.com",
                "twitter": "https://www.twitter.com",
                "reddit": "https://www.reddit.com",
            }

            if target in web_map:
                return {
                    "type": "command",
                    "command": "open_website",
                    "parameters": {"url": web_map[target]}
                }

            # URL detection
            if "." in target and " " not in target:
                url = target if target.startswith("http") else f"https://{target}"
                return {
                    "type": "command",
                    "command": "open_website",
                    "parameters": {"url": url}
                }

            # App detection
            app_map = {
                "chrome": "chrome", "browser": "chrome",
                "notepad": "notepad", "calculator": "calc",
                "code": "code", "vscode": "code", "vs code": "code",
                "word": "winword", "excel": "excel",
                "outlook": "outlook", "explorer": "explorer",
            }
            if target in app_map:
                return {
                    "type": "command",
                    "command": "open_application",
                    "parameters": {"name": app_map[target]}
                }

        # Close application
        if t.startswith("close ") or t.startswith("terminate "):
            target = t.replace("close ", "").replace("terminate ", "").strip().split()[0]
            return {
                "type": "command",
                "command": "close_application",
                "parameters": {"name": target}
            }

        # System queries
        system_keywords = {
            "cpu": "cpu", "ram": "ram", "memory": "ram",
            "battery": "battery", "disk": "disk"
        }
        if any(kw in t for kw in ["cpu usage", "ram usage", "battery level", "system stats", "memory usage", "disk space"]):
            query = "general"
            for kw, val in system_keywords.items():
                if kw in t:
                    query = val
                    break
            return {
                "type": "command",
                "command": "system_query",
                "parameters": {"query": query}
            }

        # Screenshot
        if "screenshot" in t or "capture screen" in t:
            return {
                "type": "command",
                "command": "screenshot",
                "parameters": {}
            }

        # YouTube play - instant detection (bilingual)
        youtube_triggers = [
            (r"(?:play|search|find|watch|put on)\s+(.+?)(?:\s+on\s+youtube|\s+في\s+يوتيوب|\s+يوتوب)?$", None),
            (r"(?:شغل|ابحث عن|افتح)\s+(.+?)(?:\s+(?:في|على|من)\s+(?:يوتيوب|يوتوب))?$", None),
            (r"(?:play|شغل)\s+(.+)", None),
        ]
        # Check if it references YouTube explicitly
        is_youtube = any(yt in t for yt in ["youtube", "يوتيوب", "يوتوب"])
        if is_youtube:
            for pattern, _ in youtube_triggers:
                match = re.search(pattern, t, re.IGNORECASE)
                if match:
                    query = match.group(1).strip()
                    # Remove "on youtube" etc. from the query
                    for remove in ["on youtube", "في يوتيوب", "في يوتوب", "على يوتيوب", "من يوتيوب"]:
                        query = query.replace(remove, "").strip()
                    if query:
                        return {
                            "type": "command",
                            "command": "play_youtube_video",
                            "parameters": {"query": query}
                        }

        # Email
        if "email" in t or "mail" in t:
            recipient = ""
            match = re.search(r'[\w\.-]+@[\w\.-]+', original)
            if match:
                recipient = match.group(0)
            
            # If we have a recipient but it's just a general "send email", Gemini is better
            # but for a quick "email x@y.com", this works.
            if recipient:
                return {
                    "type": "command",
                    "command": "send_email",
                    "parameters": {"recipient": recipient}
                }
            
        return None
