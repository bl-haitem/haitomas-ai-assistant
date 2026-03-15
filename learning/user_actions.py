import json
import os
from datetime import datetime

class LearningSystem:
    def __init__(self, log_file="learning/user_history.json"):
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def log_action(self, command, actions):
        """Saves user commands and the resulting AI plan for later training/refinement."""
        try:
            with open(self.log_file, "r") as f:
                history = json.load(f)
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "actions": actions
            }
            history.append(entry)
            
            with open(self.log_file, "w") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"Learning error: {e}")

    def get_recent_history(self, limit=5):
        """Returns the last few interactions to provide context to the AI."""
        try:
            if not os.path.exists(self.log_file): return []
            with open(self.log_file, "r") as f:
                history = json.load(f)
            return history[-limit:]
        except:
            return []
