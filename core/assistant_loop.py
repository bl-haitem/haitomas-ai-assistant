"""
HAITOMAS ASSISTANT — Assistant Loop
The central processing loop that ties everything together.
"""
import threading
import sys
import time
import config.settings as settings
from brain.gemini_controller import GeminiController
from brain.intent_analyzer import IntentAnalyzer
from brain.context_manager import ContextManager
from core.action_interpreter import ActionInterpreter
from core.command_router import CommandRouter
from core.workflow_executor import WorkflowExecutor
from core.code_executor import CodeExecutor
from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK, EVENT_ERROR
from automation.system_control import SystemControl
from automation.mouse_keyboard import MouseKeyboard
from automation.browser_control import BrowserControl
from automation.smart_browser import SmartBrowser
from automation.file_manager import FileManager
from automation.window_manager import WindowManager
from vision.screen_analyzer import ScreenAnalyzer
from voice.text_to_speech import TextToSpeech
from memory.memory_manager import MemoryManager
from brain.researcher import Researcher
from security.permission_manager import PermissionManager
from learning.behavior_tracker import BehaviorTracker
from learning.task_optimizer import TaskOptimizer
from automation.dev_agent import DevAgent
from vision.live_analyzer import LiveAnalyzer


class AssistantLoop:
    """
    The main orchestrator. Processes user input through the full pipeline.
    """

    def __init__(self):
        print("╔═══════════════════════════════════════════╗")
        print("║   HAITOMAS ASSISTANT — Initializing...    ║")
        print("╚═══════════════════════════════════════════╝")

        # Brain
        self.gemini = GeminiController()
        self.intent = IntentAnalyzer()
        self.context = ContextManager()

        # Core
        self.interpreter = ActionInterpreter()
        self.code_executor = CodeExecutor()

        # Automation
        self.system = SystemControl()
        self.input_ctrl = MouseKeyboard()
        self.browser = BrowserControl()
        self.smart_browser = SmartBrowser()  # Intelligent browser engine
        self.files = FileManager()
        self.windows = WindowManager()

        # Vision
        self.vision = ScreenAnalyzer()
        self.live_vision = LiveAnalyzer(api_key=settings.GEMINI_API_KEY or settings.OPENROUTER_API_KEY)
        
        # Stolen Tech: Deep Automation
        self.dev_agent = DevAgent(self.gemini)

        # Voice
        self.tts = TextToSpeech()

        # Research
        from research.research_agent import ResearchAgent
        self.researcher = ResearchAgent(self.gemini)

        # Memory
        self.memory = MemoryManager()

        # Security
        self.permissions = PermissionManager()

        # Learning
        self.behavior = BehaviorTracker()
        self.optimizer = TaskOptimizer()

        # State for Idle Interaction
        self.last_activity = time.time()
        self.idle_period = 300 # 5 minutes default

        # Connect smart browser to system control
        self.system.smart_browser = self.smart_browser

        # Command Router
        self.router = CommandRouter(
            system_control=self.system,
            mouse_keyboard=self.input_ctrl,
            browser_control=self.browser,
            file_manager=self.files,
            window_manager=self.windows,
            vision=self.vision,
            voice=self.tts,
            research=self.researcher,
            code_executor=self.code_executor,
            smart_browser=self.smart_browser,
            dev_agent=self.dev_agent,
            live_vision=self.live_vision
        )

        self.workflow_exec = WorkflowExecutor(self.router)
        event_bus.subscribe(EVENT_SPEAK, self._on_speak)

        # Start Idle Monitor
        threading.Thread(target=self._idle_monitor, daemon=True).start()

        print("✅ All systems initialized.")

    def _on_speak(self, data: dict):
        text = data.get("text", "")
        if text:
            self.tts.speak(text)

    def _idle_monitor(self):
        """Monitors for long periods of silence and triggers proactive chatter."""
        while True:
            time.sleep(30) # Check every 30 seconds
            if time.time() - self.last_activity > self.idle_period:
                print("[AssistantLoop] System idle. Triggering proactive interaction.")
                self.last_activity = time.time() # Reset to avoid spam
                self._trigger_proactive_chatter()

    def _trigger_proactive_chatter(self):
        """Asks Gemini for a brief proactive statement."""
        prompt = "The user has been idle. As HAITOMAS (Elite AI Commander), provide a very brief (max 15 words) interesting fact, system update, or greeting to engage the user. Be concise."
        try:
            # We bypass the full pipeline for efficiency
            response = self.gemini.send_to_gemini(prompt, context="[PROACTIVE_MODE]")
            if response and response.get("type") == "conversation":
                reply = response.get("reply", "")
                if reply:
                    event_bus.publish(EVENT_SPEAK, {"text": reply})
                    event_bus.publish(EVENT_UI_UPDATE, {"text": f"🤖 Proactive: {reply}", "panel": "chat"})
        except:
            pass

    def process(self, user_input: str) -> str:
        """Main entry point for user commands."""
        self.last_activity = time.time() # Reset idle timer
        
        # New Feature: Interruptibility
        # If the AI is talking, stop it immediately when the user speaks/types
        self.tts.interrupt()

        if not user_input or not user_input.strip():
            return ""

        text = user_input.strip()
        thread = threading.Thread(target=self._process_pipeline, args=(text,), daemon=True)
        thread.start()
        return "Processing..."

    def _process_pipeline(self, text: str):
        try:
            print(f"[AssistantLoop] 🟢 New Pipeline Started: '{text}'")
            settings.reload()

            # 2. Check task optimizer cache
            cached = self.optimizer.get_cached_response(text)
            if cached:
                event_bus.publish(EVENT_UI_UPDATE, {"text": "⚡ Using optimized cached response...", "panel": "strategy"})
                self._execute_response(cached)
                return

            # 3. Try instant intent analysis
            instant = self.intent.analyze(text)
            if instant:
                event_bus.publish(EVENT_UI_UPDATE, {"text": "⚡ Instant reply detected.", "panel": "strategy"})
                result = self._execute_response(instant)
                self.memory.remember(text, instant.get("type", ""), str(result))
                return

            # Proactive Engagement Feedback (Thinking...)
            from core.voice_library import get_phrase
            lang = "ar" if any(ord(c) > 128 for c in text) else "en"
            feedback_text = get_phrase("thinking", lang)
            event_bus.publish(EVENT_SPEAK, {"text": feedback_text})

            # 4. Gemini Call
            event_bus.publish(EVENT_UI_UPDATE, {"text": f"🧠 Core reasoning engine ({lang})...", "panel": "strategy"})
            print(f"[AssistantLoop] 🧠 Calling AI model...")
            
            try:
                memory_context = self.memory.recall(text)
                lang_directive = f"[LANGUAGE: {lang.upper()}] Respond only in the {lang.upper()} language."
                context_str = self.context.get_context_string(memory_context) + "\n" + lang_directive
                
                event_bus.publish(EVENT_UI_UPDATE, {"text": f"📍 Recalling memory & context...", "panel": "strategy"})
                
                raw_response = self.gemini.send_to_gemini(text, context=context_str)
                event_bus.publish(EVENT_UI_UPDATE, {"text": "✅ Analysis complete. Validating...", "panel": "strategy"})
                print(f"[AssistantLoop] ✅ AI Response received.")
            except Exception as e:
                print(f"[AssistantLoop] ❌ AI Engine Error: {e}")
                event_bus.publish(EVENT_UI_UPDATE, {"text": f"⚠️ Reasoning failure: {e}", "panel": "strategy"})
                raise e

            # 5. Interpret & Execute
            validated = self.interpreter.interpret(raw_response)
            print(f"[AssistantLoop] ⚙️ Executing: {validated.get('type')}")
            
            self._security_check(validated)
            result = self._execute_response(validated)

            # 6. Memory & Learning
            self.context.add_command(text, validated)
            self.memory.remember(text, validated.get("type", ""), str(result))
            self.behavior.track(text, validated.get("type", ""))
            self.optimizer.register_task(text, validated)
            print(f"[AssistantLoop] 🏁 Pipeline finished.")

        except Exception as e:
            error_msg = f"Pipeline error: {e}"
            print(f"[AssistantLoop] ❌ {error_msg}")
            event_bus.publish(EVENT_ERROR, {"message": str(e)})
            event_bus.publish(EVENT_UI_UPDATE, {"text": f"❌ Error: {e}", "panel": "chat"})
            self.tts.speak("Commander, I encountered a snag in my neural link. Please try again.")

    def _execute_response(self, response: dict) -> str:
        resp_type = response.get("type", "")
        
        # PROACTIVE FILTER: Ensure we never show raw JSON logic to the user
        if resp_type == "code_execution":
            # If AI returns code_execution but it's clearly for a file/app
            desc = response.get("description", "").lower()
            if "script" in desc or "app" in desc or "file" in desc or "main.py" in desc:
                print("[AssistantLoop] 🔄 Redirecting code_execution to build_project for persistent storage...")
                response["type"] = "command"
                response["command"] = "build_project"
                response["parameters"] = {"description": response.get("description", "Building user script"), "language": response.get("language", "python")}

        if resp_type == "workflow":
            return self.workflow_exec.execute(response)
        elif resp_type == "clarification":
            reply = response.get("reply", "I need more information.")
            event_bus.publish(EVENT_SPEAK, {"text": reply})
            event_bus.publish(EVENT_UI_UPDATE, {"text": reply, "panel": "chat"})
            return reply
        elif resp_type == "conversation":
            # Extra safety: Ensure reply isn't a stringified dict
            reply = response.get("reply", "")
            if reply.strip().startswith("{") and "type" in reply:
                 try:
                     # If the AI accidentally put JSON in the reply field, parse and route it
                     nested = json.loads(reply)
                     return self._execute_response(nested)
                 except: pass
            return self.router.route(response)
        else:
            return self.router.route(response)

    def _security_check(self, response: dict):
        resp_type = response.get("type", "")
        if resp_type == "command":
            command = response.get("command", "")
            target = str(response.get("parameters", {}))
            level, msg = self.permissions.check(command, target)
            if level == "FORBIDDEN":
                raise PermissionError(msg)
        elif resp_type == "code_execution":
            from security.safety_guard import SafetyGuard
            guard = SafetyGuard()
            code = response.get("code", "")
            is_safe, msg = guard.validate_code(code)
            if not is_safe:
                raise PermissionError(msg)
