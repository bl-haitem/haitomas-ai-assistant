import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer

class SemanticMemory:
    """Memory & Learning System (Layer 7).
    Uses FAISS for high-speed semantic retrieval of past tasks and preferences.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index_path = "brain/memory.index"
        self.meta_path = "brain/memory_metadata.json"
        self.dimension = 384 # Dimension for all-MiniLM-L6-v2
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r") as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def store(self, command, plan, intent="task"):
        """Stores a command and its execution plan semantically."""
        vector = self.model.encode([command])[0].astype('float32')
        self.index.add(np.array([vector]))
        
        self.metadata.append({
            "command": command,
            "plan": plan,
            "intent": intent,
            "timestamp": os.path.getmtime(self.meta_path) if os.path.exists(self.meta_path) else 0
        })
        
        # Persist
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w") as f:
            json.dump(self.metadata, f)

    def search(self, query, top_k=3):
        """Retrieves the most semantically similar past experiences."""
        if self.index.ntotal == 0:
            return []
            
        vector = self.model.encode([query])[0].astype('float32')
        distances, indices = self.index.search(np.array([vector]), top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

    def get_context(self, query):
        """Generates a summary of past relevant actions for the AI prompt."""
        past = self.search(query)
        if not past: return ""
        
        ctx = "\nPAST RELEVANT EXPERIENCES:\n"
        for p in past:
            ctx += f"- User: {p['command']} -> Response: {p['plan']}\n"
        return ctx
