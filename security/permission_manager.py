"""
HAITOMAS ASSISTANT — Permission Manager
Defines and enforces permission levels for system operations.
"""


class PermissionManager:
    """Manages operation permissions with 3 security levels."""

    # Level 1: Safe (auto-execute)
    SAFE_ACTIONS = {
        "open_application", "open_website", "web_search", "system_query",
        "media_control", "screenshot", "read_screen", "conversation",
        "knowledge", "type_text", "press_key", "navigate",
    }

    # Level 2: Requires confirmation
    CONFIRM_ACTIONS = {
        "manage_file", "code_execution", "close_application",
        "generate_pdf", "hotkey",
    }

    # Level 3: Restricted/Forbidden
    FORBIDDEN_PATTERNS = [
        "system32", "windows\\system", "program data",
        "format c:", "rd /s", "del /f /s",
        "shutdown", "restart", "reboot",
        "registry", "regedit", "reg delete",
    ]

    def check(self, action: str, target: str = "") -> tuple:
        """
        Check if an action is allowed.
        Returns: (level, message)
        - level: "SAFE", "CONFIRM", "FORBIDDEN"
        """
        # Check forbidden patterns first
        combined = f"{action} {target}".lower()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in combined:
                return "FORBIDDEN", f"Action blocked: '{pattern}' matches a restricted pattern."

        # Check action level
        if action in self.SAFE_ACTIONS:
            return "SAFE", "Operation allowed."

        if action in self.CONFIRM_ACTIONS:
            return "CONFIRM", f"Action '{action}' requires user confirmation."

        # Unknown actions default to confirm
        return "CONFIRM", f"Unknown action '{action}' — requesting confirmation."
