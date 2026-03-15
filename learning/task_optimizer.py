"""
HAITOMAS ASSISTANT — Task Optimizer
Optimizes repeated tasks by learning from user patterns.
"""
import json
import os
from config.settings import PROJECT_ROOT


class TaskOptimizer:
    """Learns from repeated tasks to suggest optimizations."""

    def __init__(self):
        self.cache_file = os.path.join(PROJECT_ROOT, "learning", "task_cache.json")
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        self.cache = self._load()

    def register_task(self, command: str, result: dict):
        """Register a successfully completed task for future optimization."""
        key = self._normalize(command)
        self.cache[key] = {
            "original_command": command,
            "response": result,
            "count": self.cache.get(key, {}).get("count", 0) + 1
        }
        self._save()

    def get_cached_response(self, command: str) -> dict | None:
        """Check if we have a cached response for a similar task."""
        key = self._normalize(command)
        cached = self.cache.get(key)
        if cached and cached.get("count", 0) >= 3:
            # Only use cache if the task has been done 3+ times
            return cached.get("response")
        return None

    def get_suggestions(self, command: str) -> list:
        """Suggest similar past commands."""
        key = self._normalize(command)
        suggestions = []
        for cached_key, data in self.cache.items():
            if key[:10] in cached_key or cached_key[:10] in key:
                suggestions.append(data.get("original_command", ""))
        return suggestions[:5]

    def _normalize(self, text: str) -> str:
        """Normalize command for matching."""
        return " ".join(text.lower().strip().split())

    def _load(self) -> dict:
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2, default=str)
        except Exception as e:
            print(f"[TaskOptimizer] Save error: {e}")
