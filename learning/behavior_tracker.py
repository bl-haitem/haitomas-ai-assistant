"""
HAITOMAS ASSISTANT — Behavior Tracker
Tracks user behavior patterns to optimize the assistant over time.
"""
import json
import os
from collections import Counter
from datetime import datetime
from config.settings import PROJECT_ROOT


class BehaviorTracker:
    """Tracks user patterns for personalization and optimization."""

    def __init__(self):
        self.data_file = os.path.join(PROJECT_ROOT, "learning", "behavior_data.json")
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        self.data = self._load()

    def track(self, command: str, response_type: str):
        """Track a user command."""
        hour = datetime.now().hour
        day = datetime.now().strftime("%A")

        self.data.setdefault("commands", [])
        self.data.setdefault("hourly_activity", {})
        self.data.setdefault("daily_activity", {})
        self.data.setdefault("type_frequency", {})

        self.data["commands"].append({
            "command": command,
            "type": response_type,
            "time": datetime.now().isoformat()
        })
        # Keep last 1000
        self.data["commands"] = self.data["commands"][-1000:]

        # Hourly activity
        h_key = str(hour)
        self.data["hourly_activity"][h_key] = self.data["hourly_activity"].get(h_key, 0) + 1

        # Daily activity
        self.data["daily_activity"][day] = self.data["daily_activity"].get(day, 0) + 1

        # Type frequency
        self.data["type_frequency"][response_type] = self.data["type_frequency"].get(response_type, 0) + 1

        self._save()

    def get_top_commands(self, limit: int = 10) -> list:
        """Get most frequently used commands."""
        cmds = [c["command"] for c in self.data.get("commands", [])]
        return Counter(cmds).most_common(limit)

    def get_active_hours(self) -> dict:
        """Get activity by hour of day."""
        return self.data.get("hourly_activity", {})

    def get_summary(self) -> dict:
        """Get a behavioral summary."""
        return {
            "total_interactions": len(self.data.get("commands", [])),
            "top_commands": self.get_top_commands(5),
            "type_frequency": self.data.get("type_frequency", {}),
            "active_hours": self.get_active_hours()
        }

    def _load(self) -> dict:
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"[BehaviorTracker] Save error: {e}")
