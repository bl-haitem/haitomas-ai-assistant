import json
import os
from typing import List, Dict, Any
from core.skill import Skill

class MemorySkill(Skill):
    """Modular Skill for Persistent Fact Management (Layer 7)."""
    
    def __init__(self):
        self.memory_file = "brain/explicit_memory.json"
        self._ensure_file()

    @property
    def name(self) -> str:
        return "memory_skill"

    def _ensure_file(self):
        if not os.path.exists(self.memory_file):
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump({}, f)

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "remember_fact",
                "description": "Save a specific preference or fact about the user.",
                "parameters": ["key", "value"]
            },
            {
                "name": "forget_fact",
                "description": "Remove a previously stored fact.",
                "parameters": ["key"]
            },
            {
                "name": "recall_all",
                "description": "List all explicitly remembered facts.",
                "parameters": []
            }
        ]

    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        with open(self.memory_file, 'r') as f:
            memory = json.load(f)

        if action == "remember_fact":
            key = params.get("key")
            value = params.get("value")
            memory[key] = value
            result = f"Confirmed. I have archived '{key}' as '{value}' in my core database."
        
        elif action == "forget_fact":
            key = params.get("key")
            if key in memory:
                del memory[key]
                result = f"System Update: Fact '{key}' has been purged from memory."
            else:
                result = f"Error: Fact '{key}' not found."
        
        elif action == "recall_all":
            result = f"Current Knowledge Base: {json.dumps(memory, indent=2)}"
        
        else:
            return None

        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        return result
