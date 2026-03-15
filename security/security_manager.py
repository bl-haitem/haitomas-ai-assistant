import psutil

class SecurityManager:
    def __init__(self):
        self.safety_levels = {
            1: "Low - Monitor only",
            2: "Medium - Confirm file operations",
            3: "High - Block system changes"
        }
        self.current_level = 2

    def check_safety(self, action_type):
        """Returns True if action is allowed under current safety level."""
        restricted = ["delete", "format", "install", "os_change"]
        if self.current_level >= 2 and action_type in restricted:
            return False
        return True

    def monitor_resources(self):
        """Returns PC health stats."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return {"cpu": cpu, "ram": ram, "status": "Healthy" if cpu < 80 else "Overloaded"}