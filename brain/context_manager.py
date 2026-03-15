"""
HAITOMAS ASSISTANT — Context Manager
Manages conversation context, memory injection, and user session state.
"""
import json
import os
from datetime import datetime


class ContextManager:
    """Manages conversation context for Gemini prompts."""

    def __init__(self):
        self.session_start = datetime.now().isoformat()
        self.current_context = {
            "session_start": self.session_start,
            "recent_commands": [],
            "active_applications": [],
            "user_preferences": {},
            "last_error": None
        }

    def add_command(self, command: str, result: dict):
        """Track executed commands in the session."""
        self.current_context["recent_commands"].append({
            "time": datetime.now().isoformat(),
            "command": command,
            "result_type": result.get("type", "unknown")
        })
        # Keep only last 20
        self.current_context["recent_commands"] = self.current_context["recent_commands"][-20:]

    def set_error(self, error: str):
        """Track last error for debugging context."""
        self.current_context["last_error"] = {
            "time": datetime.now().isoformat(),
            "message": error
        }

    def get_context_string(self, memory_context: str = "") -> str:
        """Build a context string for Gemini prompts."""
        parts = []

        # Recent commands
        recent = self.current_context["recent_commands"][-5:]
        if recent:
            parts.append("RECENT COMMANDS:")
            for cmd in recent:
                parts.append(f"  - [{cmd['result_type']}] {cmd['command']}")

        # Memory context
        if memory_context:
            parts.append(f"\nMEMORY:\n{memory_context}")

        # Last error
        if self.current_context["last_error"]:
            err = self.current_context["last_error"]
            parts.append(f"\nLAST ERROR: {err['message']}")

        # Time context
        parts.append(f"\nCURRENT TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(parts)

    def clear_session(self):
        """Reset session state."""
        self.current_context["recent_commands"] = []
        self.current_context["last_error"] = None
