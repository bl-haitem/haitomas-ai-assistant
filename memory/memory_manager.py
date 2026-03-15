"""
HAITOMAS ASSISTANT — Memory Manager
Unified interface for all memory systems (vector store + task history).
"""
from memory.vector_store import VectorStore
from memory.task_history import TaskHistory


class MemoryManager:
    """Unified memory system combining vector search and task history."""

    def __init__(self):
        self.vectors = VectorStore()
        self.history = TaskHistory()

    def remember(self, command: str, response_type: str, result: str):
        """Store a command in both vector memory and task history."""
        # Task history (always)
        self.history.log(command, response_type, result)

        # Vector memory (for semantic search)
        self.vectors.store(command, {
            "type": response_type,
            "result": str(result)[:300]
        })

    def recall(self, query: str) -> str:
        """Retrieve relevant past context for a query."""
        # Semantic search
        vector_context = self.vectors.get_context_string(query)

        # Recent history
        recent = self.history.get_recent(5)
        history_context = ""
        if recent:
            history_context = "RECENT HISTORY:\n"
            for h in recent:
                history_context += f"  - [{h['type']}] {h['command']}\n"

        return f"{vector_context}\n{history_context}".strip()

    def get_recent_history(self, limit: int = 5) -> list:
        """Get recent task history."""
        return self.history.get_recent(limit)

    def get_stats(self) -> dict:
        """Get memory statistics."""
        return self.history.get_stats()
