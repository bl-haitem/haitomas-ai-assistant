try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

import numpy as np
import re

class SemanticRouter:
    """A high-speed semantic engine with an unbreakable fallback."""
    def __init__(self):
        self.knowledge_base = [
            {"intent": "greeting", "phrases": ["hi", "hello", "hey", "haitomas", "marhaba", "مرحبا", "سلام"]},
            {"intent": "who_are_you", "phrases": ["who are you", "what is your name", "your purpose", "من انت"]},
            {"intent": "deep_knowledge_request", "phrases": ["what is", "how does", "explain", "why", "tell me about", "معنى", "اشرح لي"]},
            {"intent": "learning_path", "phrases": ["how to learn", "become a", "study resources for", "roadmap for", "learning", "تعلم", "كيف اصبح"]},
            {"intent": "system_automation", "phrases": ["open", "launch", "run", "close", "restart", "terminate", "افتح", "اغلق", "شغل", "اوقف"]},
            {"intent": "messaging", "phrases": ["write an email", "send an email", "message", "whatsapp", "mail", "arssil", "ارسل", "اكتب ايميل"]},
            {"intent": "complex_task", "phrases": ["download and install", "search and save", "automate", "قم بـ", "حمل وثبت"]},
            {"intent": "system_report", "phrases": ["cpu", "ram", "memory", "battery", "status", "usage", "حالة الجهاز", "تقرير"]},
            {"intent": "media_control", "phrases": ["play", "stop", "pause", "music", "video"]},
            {"intent": "file_management", "phrases": ["file", "document", "pdf", "copy", "move", "ملف", "انقل"]}
        ]
        
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer()
            self._initialize_vectors()
        else:
            print("[Warning] Sklearn not found. Using Simple Keyword Routing.")

    def _initialize_vectors(self):
        all_phrases = []
        self.intent_map = []
        for item in self.knowledge_base:
            for phrase in item["phrases"]:
                all_phrases.append(phrase)
                self.intent_map.append(item["intent"])
        self.action_vectors = self.vectorizer.fit_transform(all_phrases)

    def route(self, text, threshold=0.3):
        t = text.lower()
        if SKLEARN_AVAILABLE:
            try:
                query_vec = self.vectorizer.transform([t])
                similarities = cosine_similarity(query_vec, self.action_vectors).flatten()
                best_match_idx = np.argmax(similarities)
                if similarities[best_match_idx] >= threshold:
                    return self.intent_map[best_match_idx]
            except:
                pass
        
        # Fallback: Simple Keyword Match
        for item in self.knowledge_base:
            if any(phrase in t for phrase in item["phrases"]):
                return item["intent"]
        
        return "complex_llm_task"
