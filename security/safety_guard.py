"""
HAITOMAS ASSISTANT — Safety Guard
Runtime safety checks for system resources and dangerous operations.
"""
import psutil


class SafetyGuard:
    """Runtime safety monitoring and hazard detection."""

    def __init__(self):
        self.cpu_threshold = 90
        self.ram_threshold = 90

    def check_system_health(self) -> tuple:
        """Check if system resources are within safe limits."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent

            if cpu > self.cpu_threshold or ram > self.ram_threshold:
                return False, f"System overloaded: CPU {cpu}%, RAM {ram}%"
            return True, f"System nominal: CPU {cpu}%, RAM {ram}%"
        except Exception as e:
            return True, f"Health check error: {e}"

    def validate_code(self, code: str) -> tuple:
        """Validate code before execution for dangerous patterns."""
        dangerous_patterns = [
            "os.system('rm -rf",
            "shutil.rmtree('/'",
            "format(",
            "subprocess.call(['shutdown'",
            "os.remove(", "os.unlink(",
            "__import__('os').system",
            "exec(", "eval(",
        ]

        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                return False, f"Dangerous code pattern detected: {pattern}"

        # Check for imports of dangerous modules
        dangerous_imports = ["ctypes", "winreg"]
        for imp in dangerous_imports:
            if f"import {imp}" in code:
                return False, f"Restricted import detected: {imp}"

        return True, "Code passed safety check."

    def validate_file_operation(self, operation: str, path: str) -> tuple:
        """Validate file operations for safety."""
        protected_paths = [
            "windows", "system32", "program files",
            "boot", "drivers", "etc",
        ]

        path_lower = path.lower().replace("\\", "/")
        for protected in protected_paths:
            if protected in path_lower:
                if operation in ["delete", "move", "write"]:
                    return False, f"Cannot {operation} in protected directory: {path}"

        return True, "File operation allowed."
