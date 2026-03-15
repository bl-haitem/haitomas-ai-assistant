"""
HAITOMAS ASSISTANT — Action Interpreter
Parses structured JSON from Gemini and validates actions before routing.
"""
import json


class ActionInterpreter:
    """Validates and normalizes Gemini JSON responses into executable actions."""

    VALID_TYPES = {"conversation", "knowledge", "command", "workflow", "code_execution", "clarification", "fetch_info", "browser_interaction", "play_youtube_video"}

    VALID_COMMANDS = {
        "open_application", "close_application", "open_website", "web_search",
        "system_query", "media_control", "type_text", "press_key", "hotkey",
        "screenshot", "read_screen", "generate_pdf", "manage_file",
        "capture_screen", "navigate", "send_whatsapp", "deep_search",
        "open_overleaf_with_latex", "send_email", "fetch_info", "play_youtube_video",
        # Smart Browser Commands
        "browser_click", "browser_type", "browser_scroll", "browser_back",
        "browser_forward", "browser_extract", "browser_screenshot",
        "browser_page_info", "browser_fill_form", "browser_search_site",
        "google_search", "browser_interact", "close_browser",
        # Stolen Tech: Deep Automation
        "build_project", "live_vision", "send_whatsapp_native", "send_telegram_native",
        "browser_wait"
    }

    def interpret(self, response: dict) -> dict:
        """
        Validate and normalize a Gemini response.
        Returns a clean, validated action dict.
        """
        if not isinstance(response, dict):
            return {"type": "conversation", "reply": "Received invalid response format."}

        resp_type = response.get("type", "conversation")

        # Command Normalization (Fix for models returning commands as top-level types)
        if resp_type == "play_youtube_video":
            return {
                "type": "command", 
                "command": "play_youtube_video", 
                "parameters": {"query": response.get("query") or response.get("parameters", {}).get("query", "")}
            }

        if resp_type not in self.VALID_TYPES:
            # Check if it contains a reply
            if "reply" in response:
                return {"type": "conversation", "reply": response["reply"]}
            # Generic recovery to avoid showing raw JSON
            return {"type": "conversation", "reply": "I'm processing your request. One moment."}

        if resp_type == "conversation":
            return self._validate_conversation(response)
        elif resp_type == "knowledge":
            return self._validate_knowledge(response)
        elif resp_type == "clarification":
            return self._validate_clarification(response)
        elif resp_type == "command":
            return self._validate_command(response)
        elif resp_type == "workflow":
            return self._validate_workflow(response)
        elif resp_type == "code_execution":
            return self._validate_code_execution(response)
        elif resp_type == "fetch_info":
            return self._validate_fetch_info(response)
        elif resp_type == "browser_interaction":
            return self._validate_browser_interaction(response)

        return response

    def _validate_fetch_info(self, r: dict) -> dict:
        return {
            "type": "fetch_info",
            "query": r.get("query") or r.get("parameters", {}).get("query", "current news")
        }

    def _validate_clarification(self, r: dict) -> dict:
        return {
            "type": "clarification",
            "reply": r.get("reply", "I need more information."),
            "intent": r.get("intent", ""),
            "collected_params": r.get("collected_params", {})
        }

    def _validate_conversation(self, r: dict) -> dict:
        return {
            "type": "conversation",
            "reply": r.get("reply", "I processed your request.")
        }

    def _validate_knowledge(self, r: dict) -> dict:
        return {
            "type": "knowledge",
            "topic": r.get("topic", "Unknown"),
            "reply": r.get("reply", "No information available."),
            "sources": r.get("sources", [])
        }

    def _validate_command(self, r: dict) -> dict:
        command = r.get("command", "")
        parameters = r.get("parameters", {})

        if not isinstance(parameters, dict):
            parameters = {}

        return {
            "type": "command",
            "command": command,
            "parameters": parameters
        }

    def _validate_workflow(self, r: dict) -> dict:
        steps = r.get("steps", [])
        validated_steps = []

        for step in steps:
            if isinstance(step, dict) and "action" in step:
                validated_steps.append({
                    "action": step["action"],
                    "parameters": step.get("parameters", {})
                })

        return {
            "type": "workflow",
            "goal": r.get("goal", "Multi-step task"),
            "steps": validated_steps
        }

    def _validate_code_execution(self, r: dict) -> dict:
        return {
            "type": "code_execution",
            "language": r.get("language", "python"),
            "code": r.get("code", ""),
            "description": r.get("description", "Code execution")
        }

    def _validate_browser_interaction(self, r: dict) -> dict:
        """Validate browser interaction with sequential actions."""
        actions = r.get("actions", [])
        validated_actions = []
        for action in actions:
            if isinstance(action, dict) and "action" in action:
                validated_actions.append(action)
        return {
            "type": "browser_interaction",
            "goal": r.get("goal", "Web interaction"),
            "actions": validated_actions
        }

    def _validate_play_youtube_video(self, r: dict) -> dict:
        return {
            "type": "command",
            "command": "play_youtube_video",
            "parameters": {"query": r.get("query") or r.get("parameters", {}).get("query", "")}
        }
