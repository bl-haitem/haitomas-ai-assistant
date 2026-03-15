"""
HAITOMAS ASSISTANT — Event Bus
Simple publish/subscribe event system for decoupled module communication.
"""
import threading
from collections import defaultdict
from typing import Callable


class EventBus:
    """Lightweight pub/sub event system."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._subscribers = defaultdict(list)
            return cls._instance

    def subscribe(self, event: str, callback: Callable):
        """Subscribe to an event."""
        self._subscribers[event].append(callback)

    def publish(self, event: str, data: dict = None):
        """Publish an event to all subscribers."""
        for callback in self._subscribers.get(event, []):
            try:
                threading.Thread(target=callback, args=(data or {},), daemon=True).start()
            except Exception as e:
                print(f"[EventBus] Error in {event} handler: {e}")

    def clear(self):
        """Remove all subscribers."""
        self._subscribers.clear()


# Singleton instance
event_bus = EventBus()

# Event name constants
EVENT_USER_INPUT = "user_input"
EVENT_GEMINI_RESPONSE = "gemini_response"
EVENT_COMMAND_EXECUTED = "command_executed"
EVENT_ERROR = "error"
EVENT_STATUS_UPDATE = "status_update"
EVENT_SPEAK = "speak"
EVENT_UI_UPDATE = "ui_update"
