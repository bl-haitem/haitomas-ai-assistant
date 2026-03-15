import psutil
import logging

class SafetyManager:
    """Security & Resource Manager (Layer 10).
    Ensures safe operations and monitors system health.
    """
    def __init__(self):
        self.permission_levels = {
            "safe": 1,      # Browse web, open apps, system stats
            "confirmed": 2, # Delete files, install software, system changes
            "forbidden": 3  # Critical system files, registry edits
        }
        
    def check_operation(self, action, target):
        """Verifies if an action is safe or requires confirmation."""
        confirm_words = ["delete", "remove", "install", "format", "uninstall", "kill"]
        forbidden_paths = ["windows", "system32", "program data"]
        
        # 1. Forbidden Check
        if any(p in str(target).lower() for p in forbidden_paths):
            return "FORBIDDEN", "Target path is protected by system security."
            
        # 2. Confirmation Check
        if any(w in str(action).lower() for w in confirm_words):
            return "CONFIRMATION_REQUIRED", f"This action '{action}' on '{target}' requires manual approval."
            
        return "SAFE", "Operation allowed."

    def monitor_resources(self):
        """Checks if the system is under heavy load."""
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        
        if cpu > 90 or ram > 90:
            return False, f"System critical: CPU {cpu}%, RAM {ram}%"
        return True, "Nominal"
