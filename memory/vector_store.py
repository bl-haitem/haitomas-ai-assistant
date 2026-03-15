"""
HAITOMAS ASSISTANT — Vector Store
FAISS-based semantic vector storage for memory retrieval.
"""
import os
import json
import numpy as np
from config.settings import MEMORY_DIR


class VectorStore:
    """FAISS-powered semantic memory storage."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index_path = os.path.join(MEMORY_DIR, "memory.index")
        self.meta_path = os.path.join(MEMORY_DIR, "memory_metadata.json")
        self._model = None
        self._model_failed = False
        os.makedirs(MEMORY_DIR, exist_ok=True)

        self._load_index()

    def _get_model(self):
        """Lazy-load sentence transformer model (tries only once)."""
        if self._model is None and not self._model_failed:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                print("[VectorStore] Sentence model loaded.")
            except Exception as e:
                print(f"[VectorStore] Model unavailable — vector memory disabled. ({type(e).__name__})")
                print("[VectorStore] HINT: Run 'pip install sentence-transformers faiss-cpu' to enable advanced memory.")
                self._model_failed = True
        return self._model

    def _load_index(self):
        """Load existing FAISS index or create new one."""
        try:
            import faiss
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "r") as f:
                    self.metadata = json.load(f)
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
            self.available = True
        except ImportError:
            print("[VectorStore] FAISS not available. Memory disabled.")
            self.index = None
            self.metadata = []
            self.available = False

    def store(self, text: str, data: dict):
        """Store a text embedding with associated metadata."""
        if not self.available:
            return
        model = self._get_model()
        if model is None:
            return

        try:
            import faiss
            vector = model.encode([text])[0].astype("float32")
            self.index.add(np.array([vector]))

            entry = {"text": text, **data}
            self.metadata.append(entry)

            faiss.write_index(self.index, self.index_path)
            with open(self.meta_path, "w") as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            print(f"[VectorStore] Store error: {e}")

    def search(self, query: str, top_k: int = 3) -> list:
        """Find the most similar stored entries (with keyword fallback)."""
        if not self.available:
            return []

        model = self._get_model()
        if model:
            try:
                import faiss
                vector = model.encode([query])[0].astype("float32")
                distances, indices = self.index.search(np.array([vector]), min(top_k, self.index.ntotal))

                results = []
                for i in range(len(indices[0])):
                    idx = indices[0][i]
                    if 0 <= idx < len(self.metadata):
                        results.append({
                            "distance": float(distances[0][i]),
                            **self.metadata[idx]
                        })
                return results
            except Exception as e:
                print(f"[VectorStore] Search error: {e}")

        # Keyword fallback
        return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> list:
        """Simple keyword matching fallback."""
        query_words = set(query.lower().split())
        scored_results = []

        for entry in self.metadata:
            text = entry.get("text", "").lower()
            score = sum(1 for word in query_words if word in text)
            if score > 0:
                scored_results.append((score, entry))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:top_k]]

    def get_context_string(self, query: str) -> str:
        """Get a formatted context string from similar past entries."""
        results = self.search(query)
        if not results:
            return ""

        parts = ["PAST RELEVANT EXPERIENCES:"]
        for r in results:
            parts.append(f"  - {r.get('text', 'N/A')}: {r.get('result', 'N/A')}")
        return "\n".join(parts)
