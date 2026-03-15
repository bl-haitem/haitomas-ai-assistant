"""
HAITOMAS ASSISTANT — Gemini Controller
Primary AI reasoning engine using Google Gemini API.
All requests go through Gemini which returns structured JSON.
"""
import json
import re
import time
import requests
import sys
import ast
import config.settings as settings

# Gemini API endpoint
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

# System instruction that forces Gemini to return structured JSON
SYSTEM_INSTRUCTION = """
You are HAITOMAS, an advanced AI system operator embedded inside a user's computer.
You control the system with precision and intelligence.
You can BROWSE THE WEB like a real human — navigate, click, type, scroll, and interact with any website.

{persona}

CRITICAL RULES:
1. You MUST ALWAYS respond with valid JSON — no markdown, no extra text.
2. Every response must have a "type" field.
3. LANGUAGE CONSISTENCY: Always respond in the same language the user is speaking.
4. DIRECT EXECUTION: If the user asks to "Open", "Play", or "Go to", ALWAYS use a "type": "command" response. Never return a "type": "conversation" with JSON inside it. 
5. EMAIL DRAFTING: When asked to send an email, YOU MUST draft the entire body and subject yourself based on the user's intent if they are not provided. Be professional.
6. DYNAMIC RESPONSES: Adapt your response length to the complexity of the question.
   - For simple tasks/greetings, be concise. 
   - For complex analysis, instructions, or deep questions, provide detailed and comprehensive answers.
   - Always prioritize precision and clarity.
7. SMART BROWSING & ACTIONS:
   - If the user asks for a SPECIFIC website (e.g., "Open YouTube", "Go to Google", "haitomas.ai"), ALWAYS use "open_website" or "browser_interact". NEVER use "web_search" for a specific destination.
   - If the user asks to "Play [video name]", ALWAYS use "play_youtube_video".
   - Use "web_search" ONLY if the user is asking a general question or explicitly asks to "search for".
   - ALWAYS prioritize active interaction (clicking, playing) over just displaying results.
8. CODING EXPERTISE:
   - If the user asks to "Write code", "Create a script", "Build an app", or "Write in VS Code", ALWAYS use "type": "command" with "command": "build_project". 
   - NEVER use "type": "code_execution" for requests where the user wants the code in an editor.
   - Provide a detailed "description" parameter for the DevAgent.
   - NEVER show raw JSON or code-like dicts in your text replies.
   - ALWAYS output valid JSON with DOUBLE QUOTES. Single quotes in keys are FORBIDDEN.

ALLOWED RESPONSE TYPES:

TYPE "conversation" — for greetings, questions about yourself, casual talk:
{{"type": "conversation", "reply": "your response text"}}

TYPE "knowledge" — for factual questions, explanations, educational content:
{{"type": "knowledge", "topic": "topic name", "reply": "detailed explanation", "sources": ["source1", "source2"]}}

TYPE "clarification" — if user command is missing required info:
{{"type": "clarification", "reply": "question to ask user", "intent": "original_intent", "collected_params": {{}}}}

TYPE "command" — for single system actions:
{{"type": "command", "command": "command_name", "parameters": {{"key": "value"}}}}

Available commands:
- open_application: {{"name": "app_name"}}
- close_application: {{"name": "app_name"}}
- open_website: {{"url": "full_url_or_domain"}}
- play_youtube_video: {{"query": "video topic or name"}} — SEARCHES and PLAYS the first video automatically
- web_search: {{"query": "search text"}}
- system_query: {{"query": "cpu/ram/battery/disk"}}
- media_control: {{"action": "play/pause/next/prev/volume_up/volume_down"}}
- type_text: {{"text": "text to type"}}
- press_key: {{"key": "key_name"}}
- hotkey: {{"keys": "ctrl+c"}}
- screenshot: {{"save_path": "optional_path"}}
- read_screen: {{}}
- generate_pdf: {{"title": "...", "content": "...", "filename": "..."}}
- manage_file: {{"operation": "copy/move/delete/create", "source": "...", "destination": "..."}}
- send_whatsapp: {{"phone": "number", "message": "text"}}
- deep_search: {{"query": "search query"}}
- fetch_info: {{"query": "question or topic to fetch data for"}}
- open_overleaf_with_latex: {{"latex_content": "...", "project_name": "..."}}
- send_email: {{"recipient": "email", "subject": "...", "body": "..."}}
- build_project: {{"description": "...", "language": "python"}}
- live_vision: {{"text": "...", "source": "screen/camera"}}
- send_whatsapp_native: {{"contact": "name", "message": "text"}}
- send_telegram_native: {{"contact": "name", "message": "text"}}

SMART BROWSER COMMANDS (for interacting with websites like a human):
- browser_click: {{"target": "text of button/link to click"}} — click any element by its visible text
- browser_type: {{"field": "search/placeholder/label", "text": "what to type", "press_enter": true}}
- browser_scroll: {{"direction": "down/up", "amount": 500}}
- browser_back: {{}} — go back to previous page
- browser_forward: {{}} — go forward
- browser_extract: {{}} — extract text content of current page
- browser_screenshot: {{"path": "optional"}} — screenshot of browser
- browser_page_info: {{}} — get current page title, URL, and clickable elements
- browser_fill_form: {{"fields": {{"field1": "value1", "field2": "value2"}}, "submit": true}}
- browser_search_site: {{"site_url": "example.com", "query": "search terms"}}
- google_search: {{"query": "search text", "click_first": true}} — Google search + click first result
- browser_interact: {{"actions": [{{"action": "navigate", "url": "..."}}, {{"action": "click", "target": "..."}}, {{"action": "type", "field": "...", "text": "..."}}]}}
- close_browser: {{}} — close the smart browser

TYPE "browser_interaction" — for complex multi-step web tasks:
{{"type": "browser_interaction", "goal": "what you're doing", "actions": [
    {{"action": "navigate", "url": "https://..."}},
    {{"action": "type", "field": "search", "text": "query here", "press_enter": true}},
    {{"action": "wait", "seconds": 2}},
    {{"action": "click", "target": "first result text"}},
    {{"action": "extract"}}
]}}
Available actions in browser_interaction: navigate, click, type, scroll, wait_click, screenshot, back, extract, wait

TYPE "workflow" — for multi-step complex tasks:
{{"type": "workflow", "goal": "description", "steps": [
    {{"action": "command_name", "parameters": {{}}}},
    {{"action": "command_name", "parameters": {{}}}}
]}}

TYPE "code_execution" — when the user asks to run code or compute something:
{{"type": "code_execution", "language": "python", "code": "print('hello')", "description": "what the code does"}}

SPECIAL CAPABILITIES:
- AUTONOMOUS ENGINEERING (DevAgent): Use "build_project" to plan and create multi-file software projects on the user's desktop.
- LIVE VISION (JARVIS MODE): Use "live_vision" to analyze the screen or camera in real-time. You can see the user's code or surroundings.
- SMART WEB BROWSING (CRITICAL): You can interact with ANY website like a real person.
- NATIVE MESSAGING: Use "send_whatsapp_native" or "send_telegram_native" to control Windows desktop apps directly.
- YOUTUBE VIDEOS: When asked to play a YouTube video, use play_youtube_video.
- ACADEMIC WRITING: Use "open_overleaf_with_latex" for papers/reports.

CONTEXT INFORMATION:
- Operating System: Windows
- Available browsers: Chrome, Edge (smart browser uses its own Chromium instance)
- The user speaks English and Arabic
- Current conversation context will be provided below

REMEMBER: Output ONLY valid JSON. No explanation outside JSON. No markdown code blocks.
"""


class GeminiController:
    """Primary AI brain — sends requests to Gemini and parses structured JSON."""

    def __init__(self):
        self.conversation_history = []
        self.max_history = 10 

    def send_to_gemini(self, user_message: str, context: str = "") -> dict:
        """Send a message to Gemini API and return parsed JSON response."""
        # 1. Direct Gemini if key exists
        if settings.GEMINI_API_KEY:
            print(f"[Gemini] Attempting direct Google API...")
            result = self._call_gemini_api(user_message, context)
            if result: return result

        # 2. OpenRouter (Primary Path)
        if settings.OPENROUTER_API_KEY:
            print(f"[Gemini] Attempting OpenRouter pipeline...")
            result = self._call_openrouter(user_message, context)
            if result: return result

        # 3. Local Fallback: Ollama
        print("[Gemini] Attempting local Ollama fallback...")
        result = self._call_ollama(user_message, context)
        if result: return result

        # UI Notification for failure
        print("[Gemini] CRITICAL: All AI backends failed.")
        return {
            "type": "conversation",
            "reply": "Neural links unstable. I cannot reach any reasoning models (Gemini, OpenRouter, or Ollama). Please verify your internet connection, API keys, or credits. You can continue with system commands manually if needed, Commander."
        }

    def _call_gemini_api(self, user_message: str, context: str = "") -> dict | None:
        try:
            url = GEMINI_ENDPOINT.format(model=settings.GEMINI_MODEL, key=settings.GEMINI_API_KEY)
            payload = self._build_gemini_payload(user_message, context)
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                parsed = self._parse_response(raw_text)
                self.conversation_history.append({"user": user_message, "assistant": json.dumps(parsed)})
                return parsed
            print(f"[Gemini] API fail {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"[Gemini] Error: {e}")
        return None

    def _call_openrouter(self, user_message: str, context: str = "") -> dict | None:
        try:
            persona = settings.get_persona_prompt()
            system_text = SYSTEM_INSTRUCTION.format(persona=persona)
            if context: system_text += f"\n\nADDITIONAL CONTEXT:\n{context}"

            # Ensure we have a valid model list
            models = [
                settings.OPENROUTER_MODEL,
                "google/gemini-2.0-flash-lite-preview-02-05:free",
                "google/gemini-2.0-pro-exp-02-05:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "deepseek/deepseek-chat",
                "mistralai/mistral-7b-instruct:free",
                "openrouter/auto"
            ]
            models = list(dict.fromkeys(m for m in models if m)) # Unique and non-empty

            # Messages
            messages = [{"role": "system", "content": system_text}]
            for entry in self.conversation_history[-self.max_history:]:
                messages.append({"role": "user", "content": entry["user"]})
                try: 
                    msg_data = json.loads(entry["assistant"])
                    msg = msg_data.get("reply", str(msg_data))
                except: 
                    msg = entry["assistant"]
                messages.append({"role": "assistant", "content": str(msg)})
            messages.append({"role": "user", "content": user_message})

            for model_id in models:
                # Try JSON and then Non-JSON
                for use_json in [True, False]:
                    try:
                        print(f"[OpenRouter] Trying {model_id} (JSON={use_json})")
                        payload = {"model": model_id, "messages": messages}
                        if use_json: payload["response_format"] = {"type": "json_object"}

                        response = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                                "Content-Type": "application/json",
                                "HTTP-Referer": "https://haitomas.ai",
                                "X-Title": "HAITOMAS"
                            },
                            json=payload, timeout=20 # Faster timeout
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "choices" in data and len(data["choices"]) > 0:
                                raw = data["choices"][0]["message"]["content"]
                                parsed = self._parse_response(raw)
                                self.conversation_history.append({"user": user_message, "assistant": json.dumps(parsed)})
                                print(f"[OpenRouter] SUCCESS with {model_id}")
                                return parsed
                        elif response.status_code in [401, 403]:
                            print(f"[OpenRouter] Auth/Credit error ({response.status_code}). Check your API key or credits.")
                            break # Try next model anyway, in case it's a model-specific restriction
                        elif response.status_code == 400 and use_json:
                            continue # Try non-json for this model
                        else:
                            print(f"[OpenRouter] {model_id} failed ({response.status_code}): {response.text[:100]}")
                            break # Try next model
                    except Exception as e:
                        print(f"[OpenRouter] {model_id} error: {e}")
                        break
        except Exception as e:
            print(f"[OpenRouter] Global error: {e}")
        return None

    def _call_ollama(self, user_message: str, context: str = "") -> dict | None:
        try:
            prompt = f"System: {SYSTEM_INSTRUCTION}\nUser: {user_message}\nResponse (JSON):"
            response = requests.post("http://localhost:11434/api/generate", json={"model": "phi3", "prompt": prompt, "stream": False, "format": "json"}, timeout=30)
            if response.status_code == 200:
                return self._parse_response(response.json().get("response", "{}"))
        except: pass
        return None

    def _parse_response(self, raw_text: str) -> dict:
        """Robustly extract and parse JSON from AI response."""
        try:
            # Clean up the text
            clean = raw_text.strip()
            
            # Extract only the JSON part using regex if needed
            match = re.search(r'(\{.*\})', clean, re.DOTALL)
            if match:
                clean = match.group(1)
            else:
                # If no brackets found, it might be raw text
                return {"type": "conversation", "reply": raw_text}

            # 1. Normal JSON attempt
            try:
                parsed = json.loads(clean)
                if isinstance(parsed, dict): return parsed
            except: pass

            # 2. Python ast literal_eval for single quote JSON
            try:
                parsed = ast.literal_eval(clean)
                if isinstance(parsed, dict): return parsed
            except: pass

            # 3. Final cleanup attempt
            clean_fixed = clean.replace("'", '"')
            clean_fixed = re.sub(r',\s*\}', '}', clean_fixed)
            return json.loads(clean_fixed)

        except Exception as e:
            print(f"[Gemini] Parsing Error: {e} | Raw text preview: {raw_text[:200]}")
            return {"type": "conversation", "reply": raw_text[:1000]}

    def _build_gemini_payload(self, user_message: str, extra_context: str = "") -> dict:
        persona = settings.get_persona_prompt()
        system_text = SYSTEM_INSTRUCTION.format(persona=persona)
        if extra_context: system_text += f"\n\nCONTEXT:\n{extra_context}"
        contents = []
        for entry in self.conversation_history[-self.max_history:]:
            contents.append({"role": "user", "parts": [{"text": entry["user"]}]})
            contents.append({"role": "model", "parts": [{"text": entry["assistant"]}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})
        return {
            "system_instruction": {"parts": [{"text": system_text}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"}
        }

    def quick_ask(self, question: str) -> str:
        """Quick question to AI — returns plain text. Uses fallbacks."""
        print(f"[Gemini] Performing quick_ask for: {question[:50]}...")
        
        # 1. Try Direct Gemini
        if settings.GEMINI_API_KEY:
            try:
                url = GEMINI_ENDPOINT.format(model=settings.GEMINI_MODEL, key=settings.GEMINI_API_KEY)
                resp = requests.post(url, json={"contents": [{"role": "user", "parts": [{"text": question}]}]}, timeout=20)
                if resp.status_code == 200:
                    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            except: pass

        # 2. Try OpenRouter (Multiple models)
        if settings.OPENROUTER_API_KEY:
            models = [
                settings.OPENROUTER_MODEL,
                "google/gemini-2.0-flash-exp:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "google/gemma-3-27b-it:free"
            ]
            models = list(dict.fromkeys(m for m in models if m))
            
            for m in models:
                try:
                    print(f"  [QuickAsk] Trying {m}...")
                    resp = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                        json={"model": m, "messages": [{"role": "user", "content": question}]},
                        timeout=20
                    )
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"].strip()
                except: continue

        return "Intelligence system overloaded. Unable to synthesize data at this moment."

    def clear_history(self):
        self.conversation_history.clear()
