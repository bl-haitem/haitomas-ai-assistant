"""
HAITOMAS ASSISTANT — Command Router
Routes validated actions to the appropriate automation subsystem.
Now includes smart browser interactions for real web navigation.
"""
import threading
from core.event_bus import event_bus, EVENT_COMMAND_EXECUTED, EVENT_SPEAK, EVENT_UI_UPDATE, EVENT_ERROR


class CommandRouter:
    """Dispatches parsed actions to the correct subsystem executor."""

    def __init__(self, system_control, mouse_keyboard, browser_control,
                 file_manager, window_manager, vision, voice, research, code_executor,
                 smart_browser=None, dev_agent=None, live_vision=None):
        self.system = system_control
        self.input = mouse_keyboard
        self.browser = browser_control
        self.files = file_manager
        self.windows = window_manager
        self.vision = vision
        self.voice = voice
        self.research = research
        self.code_executor = code_executor
        self.smart_browser = smart_browser
        self.dev_agent = dev_agent
        self.live_vision = live_vision

    def route(self, action: dict) -> str:
        """Route a single action to the correct handler. Returns result string."""
        action_type = action.get("type", "")

        try:
            if action_type == "conversation":
                return self._handle_conversation(action)
            elif action_type == "knowledge":
                return self._handle_knowledge(action)
            elif action_type == "command" or action_type == "play_youtube_video":
                # Some models might misclassify play_youtube_video as its own type
                if action_type == "play_youtube_video":
                    query = action.get("query") or action.get("parameters", {}).get("query", "")
                    action = {"type": "command", "command": "play_youtube_video", "parameters": {"query": query}}
                return self._handle_command(action)
            elif action_type == "fetch_info":
                result = self.research.quick_search(action.get("query", ""))
                event_bus.publish(EVENT_UI_UPDATE, {"text": result, "panel": "chat"})
                return result
            elif action_type == "code_execution":
                return self._handle_code_execution(action)
            elif action_type == "browser_interaction":
                return self._handle_browser_interaction(action)
            else:
                return f"Unknown action type: {action_type}"
        except Exception as e:
            error_msg = f"Execution error: {e}"
            event_bus.publish(EVENT_ERROR, {"message": error_msg})
            return error_msg

    def _handle_conversation(self, action: dict) -> str:
        reply = action.get("reply", "")
        event_bus.publish(EVENT_SPEAK, {"text": reply})
        event_bus.publish(EVENT_UI_UPDATE, {"text": reply, "panel": "chat"})
        return reply

    def _handle_knowledge(self, action: dict) -> str:
        topic = action.get("topic", "")
        reply = action.get("reply", "")
        sources = action.get("sources", [])

        full_reply = f"📚 {topic.upper()}\n\n{reply}"
        if sources:
            full_reply += "\n\n📎 Sources:\n" + "\n".join(f"  • {s}" for s in sources)

        event_bus.publish(EVENT_SPEAK, {"text": reply})
        event_bus.publish(EVENT_UI_UPDATE, {"text": full_reply, "panel": "strategy"})
        return full_reply

    def _handle_command(self, action: dict) -> str:
        command = action.get("command", "")
        params = action.get("parameters", {})

        result = "Command not recognized."

        if command == "open_application":
            result = self.system.open_app(params.get("name", ""))
        elif command == "close_application":
            result = self.system.close_app(params.get("name", ""))
        elif command == "open_website":
            # Use smart browser if available for richer interaction
            url = params.get("url", "")
            if self.smart_browser:
                result = self.smart_browser.navigate_to(url)
            else:
                result = self.system.web_open(url)
        elif command == "web_search":
            query = params.get("query", "")
            if self.smart_browser:
                result = self.smart_browser.google_search_and_click(query)
            else:
                result = self.system.web_search(query)
        elif command == "system_query":
            result = self.system.system_query(params.get("query", ""))
        elif command == "media_control":
            result = self.system.media_control(params.get("action", ""))
        elif command == "type_text":
            result = self.input.type_text(params.get("text", ""))
        elif command == "press_key":
            result = self.input.press_key(params.get("key", ""))
        elif command == "hotkey":
            result = self.input.hotkey(params.get("keys", ""))
        elif command == "screenshot":
            result = self.vision.capture_screen(params.get("save_path", ""))
        elif command == "read_screen":
            result = self.vision.read_screen_text()
        elif command == "generate_pdf":
            result = self.system.generate_pdf(
                params.get("title", "Report"),
                params.get("content", ""),
                params.get("filename", "report")
            )
        elif command == "manage_file":
            result = self.files.manage(
                params.get("operation", ""),
                params.get("source", ""),
                params.get("destination", "")
            )
        elif command == "navigate":
            if self.smart_browser:
                result = self.smart_browser.navigate_to(params.get("url", ""))
            else:
                result = self.browser.navigate(params.get("url", ""))
        elif command == "send_whatsapp":
            result = self.system.send_whatsapp(
                params.get("phone") or params.get("receiver", ""),
                params.get("message", "")
            )
        elif command == "deep_search":
            result = self.research.deep_search(params.get("query", ""))
        elif command == "quick_search" or command == "fetch_info":
            result = self.research.quick_search(params.get("query", ""))
        elif command == "open_overleaf_with_latex":
            result = self.system.open_overleaf_with_latex(
                params.get("latex_content", ""),
                params.get("project_name", "Academic_Paper")
            )
        elif command == "send_email":
            result = self.system.send_email(
                params.get("recipient") or params.get("to", ""),
                params.get("subject", ""),
                params.get("body", "") or params.get("message", "")
            )
        elif command == "play_youtube_video":
            result = self.system.play_youtube_video(params.get("query", ""))
        elif command == "conversation" or command == "speak":
            result = self._handle_conversation({"reply": params.get("reply") or params.get("text", "")})
        # ═══════════════════════════════════════════════════════
        # NEW: Smart Browser Commands
        # ═══════════════════════════════════════════════════════
        elif command == "browser_click":
            if self.smart_browser:
                result = self.smart_browser.click_element(params.get("target", ""))
            else:
                result = "Smart browser not available."
        elif command == "browser_type":
            if self.smart_browser:
                result = self.smart_browser.type_text_in_field(
                    params.get("field", ""),
                    params.get("text", ""),
                    params.get("press_enter", True)
                )
            else:
                result = "Smart browser not available."
        elif command == "browser_scroll":
            if self.smart_browser:
                result = self.smart_browser.scroll_page(
                    params.get("direction", "down"),
                    params.get("amount", 500)
                )
            else:
                result = "Smart browser not available."
        elif command == "browser_back":
            if self.smart_browser:
                result = self.smart_browser.go_back()
            else:
                result = "Smart browser not available."
        elif command == "browser_forward":
            if self.smart_browser:
                result = self.smart_browser.go_forward()
            else:
                result = "Smart browser not available."
        elif command == "browser_extract":
            if self.smart_browser:
                result = self.smart_browser.extract_page_content()
            else:
                result = "Smart browser not available."
        elif command == "browser_screenshot":
            if self.smart_browser:
                result = self.smart_browser.take_screenshot(params.get("path"))
            else:
                result = "Smart browser not available."
        elif command == "browser_page_info":
            if self.smart_browser:
                import json
                info = self.smart_browser.get_page_info()
                result = json.dumps(info, ensure_ascii=False, indent=2)
            else:
                result = "Smart browser not available."
        elif command == "browser_fill_form":
            if self.smart_browser:
                result = self.smart_browser.fill_form(
                    params.get("fields", {}),
                    params.get("submit", True)
                )
            else:
                result = "Smart browser not available."
        elif command == "browser_search_site":
            if self.smart_browser:
                result = self.smart_browser.search_on_site(
                    params.get("site_url", ""),
                    params.get("query", "")
                )
            else:
                result = "Smart browser not available."
        elif command == "google_search":
            if self.smart_browser:
                result = self.smart_browser.google_search_and_click(
                    params.get("query", ""),
                    params.get("click_first", True)
                )
            else:
                result = self.system.web_search(params.get("query", ""))
        elif command == "browser_interact":
            if self.smart_browser:
                result = self.smart_browser.interact_with_page(
                    params.get("actions", [])
                )
            else:
                result = "Smart browser not available."
        elif command == "close_browser":
            if self.smart_browser:
                result = self.smart_browser.close()
            else:
                result = "Smart browser not available."
        # ═══════════════════════════════════════════════════════
        # STOLEN TECH: Deep Automation
        # ═══════════════════════════════════════════════════════
        elif command == "build_project" and self.dev_agent:
            result = self.dev_agent.build_project(
                params.get("description", ""),
                params.get("language", "python")
            )
        elif command == "live_vision" and self.live_vision:
            result = self.live_vision.analyze_now(
                params.get("text", "What do you see?"),
                params.get("source", "screen")
            )
        elif command == "send_whatsapp_native":
            result = self.system.send_whatsapp_native(
                params.get("contact") or params.get("receiver", ""),
                params.get("message", "")
            )
        elif command == "send_telegram_native":
            result = self.system.send_telegram_native(
                params.get("contact") or params.get("receiver", ""),
                params.get("message", "")
            )

        event_bus.publish(EVENT_COMMAND_EXECUTED, {"command": command, "result": result})
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"✅ {command}: {result}", "panel": "chat"})
        return result

    def _handle_browser_interaction(self, action: dict) -> str:
        """Handle complex browser interaction sequences from AI."""
        if not self.smart_browser:
            return "Smart browser engine not available."
        
        actions = action.get("actions", [])
        goal = action.get("goal", "Browser interaction")
        
        event_bus.publish(EVENT_UI_UPDATE, {
            "text": f"🌐 New Browser Task: {goal}",
            "panel": "strategy"
        })
        
        # Execute actions one by one and update UI for progress
        total_results = []
        for i, act in enumerate(actions):
            act_name = act.get("action", "step")
            event_bus.publish(EVENT_UI_UPDATE, {
                "text": f"📍 Step {i+1}/{len(actions)}: {act_name}",
                "panel": "strategy"
            })
            
            # Execute single action via interact_with_page wrapper
            res = self.smart_browser.interact_with_page([act])
            total_results.append(res)
            
            # Brief check for critical errors
            if "Error" in res or "failed" in res.lower():
                event_bus.publish(EVENT_UI_UPDATE, {"text": f"⚠️ Issue: {res}", "panel": "strategy"})

        result = " | ".join(total_results)
        
        event_bus.publish(EVENT_COMMAND_EXECUTED, {"command": "browser_interaction", "result": result})
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"✅ {goal} complete.", "panel": "chat"})
        return result

    def _handle_code_execution(self, action: dict) -> str:
        language = action.get("language", "python")
        code = action.get("code", "")
        description = action.get("description", "Code execution")

        event_bus.publish(EVENT_UI_UPDATE, {"text": f"⚡ Running code: {description}", "panel": "strategy"})

        result = self.code_executor.execute(code, language)

        event_bus.publish(EVENT_UI_UPDATE, {"text": f"📤 Code Output:\n{result}", "panel": "strategy"})
        event_bus.publish(EVENT_SPEAK, {"text": f"Code execution complete. {description}"})
        return result
