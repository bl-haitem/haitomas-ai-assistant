import requests
import json
import os
from brain.semantic_memory import SemanticMemory

class AIEngine:
    def __init__(self, model="phi3", base_url="http://localhost:11434/api/generate"):
        self.model = model
        self.base_url = base_url
        self.config_path = "config/config.json"
        self.load_config()
        self.memory = SemanticMemory()
        self.load_modular_skills()

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        except:
            self.config = {"openrouter_api_key": "", "active_persona": "Assistant", "personas": {"Assistant": {"mentality": "Fast AI"}}}

    def load_modular_skills(self):
        """Discovers and loads all modular skills (JARVIS style)."""
        self.skills = {}
        # We'll manually register them for now to ensure stability
        try:
            from skills.memory_ops import MemorySkill
            from skills.vision_ops import VisionSkill
            
            ms = MemorySkill()
            vs = VisionSkill()
            
            self.skills[ms.name] = ms
            self.skills[vs.name] = vs
        except Exception as e:
            print(f"[Brain] Skill Loading Error: {e}")

    def tactical_reasoning(self, text):
        """Zero-latency pattern reasoning."""
        import re 
        t = text.lower().strip()
        
        # Pattern: Remember [X] as [Y]
        rem_match = re.search(r"(?:remember|تذكر) (?:that|بأن|أن)? (.*) (?:is|as|هو|كـ) (.*)", t)
        if rem_match:
            key, val = rem_match.groups()
            return [{"action": "memory_skill", "sub_action": "remember_fact", "param": key.strip(), "value": val.strip()}]
            
        # Pattern: Forget [X]
        for_match = re.search(r"(?:forget|انسى|أنسى) (.*)", t)
        if for_match:
            key = for_match.group(1).strip()
            return [{"action": "memory_skill", "sub_action": "forget_fact", "param": key}]

        return None

    def get_persona_prompt(self):
        persona_key = self.config.get("active_persona", "Assistant")
        persona = self.config.get("personas", {}).get(persona_key, {})
        return persona.get("mentality", "concise assistant")

    def generate_response(self, prompt, context="", smart_mode=False):
        """Unified generator supporting Local Ollama and Cloud OpenRouter."""
        api_key = self.config.get("openrouter_api_key")
        
        # Skill Context for prompt
        skill_info = "\nMODULAR SKILLS AVAILABLE:\n"
        for s_name, s_obj in self.skills.items():
            skill_info += f"- {s_name}: {json.dumps(s_obj.get_tools())}\n"

        if api_key:
            try:
                print(f"[Brain] Routing to Neural Cloud (Gemini 2.0 Flash)...")
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://haitomas.ai",
                        "X-Title": "Haitomas Assistant"
                    },
                    data=json.dumps({
                        "model": "google/gemini-2.0-flash-exp:free",
                        "messages": [
                            {"role": "system", "content": f"You are haitomas: {self.get_persona_prompt()}. {skill_info}\nPRIORITIZE ACTION OVER RESEARCH. If a task is about opening an app, file, or website, use 'open_app' or 'web_open' immediately. Do NOT initiate research for local system commands. Output RAW JSON ARRAY ONLY. Format: [{{'action': 'x', 'sub_action': 'y', 'param': 'key', 'value': 'val'}}]"},
                            {"role": "user", "content": f"Context: {context}\nTask: {prompt}"}
                        ]
                    }),
                    timeout=30
                )
                res_data = response.json()
                if 'choices' in res_data:
                    return res_data['choices'][0]['message']['content']
            except Exception as e: pass
        
        # Local Fallback
        print(f"[Brain] Local Fallback...")
        system_prompt = f"Role: {self.get_persona_prompt()}. Actions: speak, open_app, web_open, web_automation, memory_skill, system_query. IMPORTANT: If task is local (open/close/email), DO NOT use research. Output: RAW JSON ARRAY."
        payload = {
            "model": self.model,
            "prompt": f"System: {system_prompt}\nContext: {context}\nUser: {prompt}\nAssistant: [",
            "stream": False,
            "options": {"num_predict": 100, "temperature": 0.0, "stop": ["]", "User:"]}
        }
        try:
            response = requests.post(self.base_url, json=payload, timeout=25)
            text = response.json().get("response", "").strip()
            if not text.startswith("["): text = "[" + text
            return text if text.endswith("]") else text + "]"
        except Exception as e:
            return f"Brain Error: {str(e)}"

    def quick_ask(self, question, context=""):
        api_key = self.config.get("openrouter_api_key")
        if api_key:
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": "google/gemini-2.0-flash-exp:free",
                        "messages": [{"role": "user", "content": f"{context}\n\nUser: {question}"}]
                    }),
                    timeout=15
                )
                res_data = response.json()
                if 'choices' in res_data:
                    return res_data['choices'][0]['message']['content'].strip()
            except Exception as e:
                print(f"[Brain] Quick Ask Error: {e}")
        return "I am processing your request using local intelligence protocols."

    def store_experience(self, command, plan):
        self.memory.store(command, plan)

    def extract_topic(self, text):
        prompt = "Extract CORE TOPIC and intent. Format: TOPIC: [topic] | INTENT: [learning/technical/exploratory]"
        res = self.quick_ask(text, context=prompt)
        try:
            if not res or "|" not in res: return text.strip(), "exploratory"
            topic = res.split("|")[0].replace("TOPIC:", "").strip()
            intent = res.split("|")[1].replace("INTENT:", "").strip()
            return topic, intent
        except: return text.strip(), "exploratory"

    def reason_about_task(self, text):
        system_prompt = "Define Goal, Prerequisites, Safety, and Steps. Professional reasoning log only. NO JSON."
        return self.quick_ask(text, context=system_prompt)

    def plan_steps(self, user_command, context=""):
        """Unified Intelligence: Gemini decides if it's talk or an action."""
        # 1. Zero-Latency Tactical Check
        tactical_plan = self.tactical_reasoning(user_command)
        if tactical_plan: return tactical_plan

        # 2. Contextual Memory Injection
        memory_context = self.memory.get_context(user_command)
        full_context = f"SEMANTIC_MEMORY: {memory_context}\nRECENT_HISTORY: {context}"
        
        # 3. Brain Processing (Gemini-First)
        api_key = self.config.get("openrouter_api_key")
        
        # Pre-calculate skill string to avoid double-brace confusion in f-strings
        skill_str = json.dumps({n: s.get_tools() for n, s in self.skills.items()})
        
        system_instructions = f"""
        Role: You are haitomas, a high-performance system orchestrator.
        Directives:
        1. If input is conversational greeting/small talk, use action 'speak' ONLY.
        2. If input is a task (open app, search, system info, file op, email), create a multi-step execution plan.
        3. Prioritize local actions over research.
        4. Skills: {skill_str}
        5. Available Actions: speak, open_app, close_app, web_open, web_search, system_query.
        6. Output: RAW JSON ARRAY ONLY.
        Example (Talk): [{{"action": "speak", "param": "Hello Commander."}}]
        Example (Task): [{{"action": "speak", "param": "Opening email composer."}}, {{"action": "web_open", "param": "https://mail.google.com/mail/?view=cm&fs=1&to=person@example.com"}}]
        """

        if api_key:
            try:
                print(f"[Neural Pulse] Strategic Thinking on Cloud...")
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": "google/gemini-2.0-flash-exp:free",
                        "messages": [
                            {"role": "system", "content": system_instructions},
                            {"role": "user", "content": f"Context: {full_context}\nUser: {user_command}"}
                        ]
                    }),
                    timeout=30
                )
                res_data = response.json()
                if 'choices' in res_data:
                    raw_res = res_data['choices'][0]['message']['content']
                    return self._parse_json_plan(raw_res)
            except Exception as e:
                print(f"[Brain] Neural Cloud Lag: {e}")

        # 4. Local Fallback (Phi-3)
        print(f"[Brain] Transitioning to Local Synapses...")
        return self._local_plan(user_command, full_context)

    def _parse_json_plan(self, text):
        import re
        try:
            clean_json = text.strip()
            # Try to find the array first
            match = re.search(r'\[\s*\{.*\}\s*\]', clean_json, re.DOTALL)
            if match:
                clean_json = match.group(0)
            
            # Remove any markdown junk
            clean_json = clean_json.replace("```json", "").replace("```", "").strip()
            
            return json.loads(clean_json)
        except Exception as e:
            print(f"[Parser] JSON Decode Failed: {e} | Text: {text[:50]}...")
            # Fallback to a simple speak action if it's just plain text
            if len(text) > 0 and not text.startswith("["):
                return [{"action": "speak", "param": text[:300]}]
            return [{"action": "speak", "param": "My neural link returned an unformatted response. Please clarify."}]

    def _local_plan(self, command, context):
        payload = {
            "model": self.model,
            "prompt": f"User: {command}\nResponse as JSON Array (e.g. [{{'action': 'speak', 'param': '...'}}]):",
            "stream": False,
            "options": {"num_predict": 200, "temperature": 0.1}
        }
        try:
            response = requests.post(self.base_url, json=payload, timeout=20)
            res_text = response.json().get("response", "").strip()
            return self._parse_json_plan(res_text)
        except Exception as e:
            print(f"[LocalBrain] Critical Fail: {e}")
            return [{"action": "speak", "param": "Local brain offline. Ready for a new directive."}]