"""
HAITOMAS ASSISTANT — Task History
JSON-based task history for tracking all executed commands.
"""
import json
import os
from datetime import datetime
from config.settings import HISTORY_FILE


class TaskHistory:
    """Tracks all user commands and their results."""

    def __init__(self):
        self.history_file = HISTORY_FILE
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            self._save([])

    def log(self, command: str, response_type: str, result: str):
        """Log a command and its result."""
        try:
            history = self._load()
            history.append({
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "type": response_type,
                "result": str(result)[:500]  # Limit size
            })
            # Keep last 500 entries
            history = history[-500:]
            self._save(history)
        except Exception as e:
            print(f"[TaskHistory] Log error: {e}")

    def get_recent(self, limit: int = 10) -> list:
        """Get recent task history."""
        try:
            history = self._load()
            return history[-limit:]
        except Exception:
            return []

    def get_stats(self) -> dict:
        """Get usage statistics."""
        try:
            history = self._load()
            types = {}
            for entry in history:
                t = entry.get("type", "unknown")
                types[t] = types.get(t, 0) + 1
            return {
                "total_commands": len(history),
                "type_breakdown": types,
                "last_command": history[-1] if history else None
            }
        except Exception:
            return {"total_commands": 0, "type_breakdown": {}, "last_command": None}

    def search(self, query: str) -> list:
        """Search history for matching commands."""
        try:
            history = self._load()
            q = query.lower()
            return [h for h in history if q in h.get("command", "").lower()][-10:]
        except Exception:
            return []

    def _load(self) -> list:
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, data: list):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
