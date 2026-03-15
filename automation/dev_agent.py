"""
HAITOMAS ASSISTANT — Autonomous DevAgent (Smarter Version)
=========================================================
A professional project builder that plans, writes, and fixes code projects.
Inspired by Mark-XXX, enhanced for Haitomas.
"""
import os
import subprocess
import sys
from pathlib import Path
import json
import re
import ast
from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK

def robust_json_parse(text: str) -> dict:
    """Extracts and parses JSON from a string, handling common AI junk."""
    try:
        # Extract content between first { and last }
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found.")
        
        json_str = match.group(1)
        
        # 1. Direct JSON parse
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
            
        # 2. Try ast.literal_eval for single-quote 'Python-style' dicts
        try:
            # literal_eval is safer than eval but handles single quotes
            return ast.literal_eval(json_str)
        except:
            pass
            
        # 3. Final cleanup: simple string replacements for common issues
        cleaned = json_str.replace("'", '"') # Single to double
        cleaned = re.sub(r',\s*\}', '}', cleaned) # Trailing commas
        cleaned = re.sub(r',\s*\]', ']', cleaned)
        
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"Full JSON recovery failed: {e}")

class DevAgent:
    """
    Orchestrator for autonomous coding projects.
    Can plan directory structures, write files, install dependencies, 
    run the project, and self-correct errors up to 3 times.
    """

    MAX_FIX_ATTEMPTS = 3

    def __init__(self, ai_controller):
        self.ai = ai_controller
        self.projects_dir = Path.home() / "Desktop" / "HaitomasProjects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def build_project(self, description: str, language: str = "python") -> str:
        """EntryPoint: Full cycle of project building."""
        event_bus.publish(EVENT_UI_UPDATE, {"text": f"🛠️ Starting DevAgent: {description[:50]}...", "panel": "strategy"})
        
        try:
            # 1. Plan
            plan = self._plan_project(description, language)
            project_name = plan.get("project_name", "haitomas_app")
            project_path = self.projects_dir / project_name
            project_path.mkdir(parents=True, exist_ok=True)
            
            event_bus.publish(EVENT_UI_UPDATE, {"text": f"📋 Plan generated: {len(plan['files'])} files target.", "panel": "strategy"})
            
            # 2. Write Files
            for file_info in plan["files"]:
                event_bus.publish(EVENT_UI_UPDATE, {"text": f"✍️ Writing: {file_info['path']}", "panel": "strategy"})
                self._write_file(file_info, plan, project_path, language)
            
            # 3. Dependencies
            if plan.get("dependencies"):
                event_bus.publish(EVENT_UI_UPDATE, {"text": f"📦 Installing requirements...", "panel": "strategy"})
                self._install_deps(plan["dependencies"], project_path)
            
            # 4. Self-Fixing Loop
            entry_point = plan.get("entry_point", "main.py")
            run_cmd = plan.get("run_command") or f"python {entry_point}"
            
            fix_count = 0
            while fix_count < self.MAX_FIX_ATTEMPTS:
                event_bus.publish(EVENT_UI_UPDATE, {"text": f"🚀 Running verification (Attempt {fix_count+1})...", "panel": "strategy"})
                success, output = self._test_run(run_cmd, project_path)
                
                if success:
                    event_bus.publish(EVENT_UI_UPDATE, {"text": "✅ Verification passed! No critical errors.", "panel": "strategy"})
                    break
                else:
                    fix_count += 1
                    event_bus.publish(EVENT_UI_UPDATE, {"text": f"⚠️ Bug detected. Fix attempt {fix_count}/{self.MAX_FIX_ATTEMPTS}...", "panel": "strategy"})
                    self._fix_project(output, project_path, plan, language)
            
            result_msg = f"✅ Project '{project_name}' ready at {project_path}."
            event_bus.publish(EVENT_SPEAK, {"text": "Project built and verified, Commander. Opening in Visual Studio Code."})
            
            # Open in VS Code automatically (with robust path detection)
            try:
                # 1. Try generic 'code' command
                proc = subprocess.Popen(f'code "{project_path}"', shell=True)
                
                # 2. Fallback for Windows if 'code' command isn't in PATH
                if os.name == 'nt':
                     vscode_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd")
                     if os.path.exists(vscode_path):
                         subprocess.Popen(f'"{vscode_path}" "{project_path}"', shell=True)
            except: pass
            
            return result_msg
            
        except Exception as e:
            error_msg = f"❌ DevAgent failed: {e}"
            event_bus.publish(EVENT_UI_UPDATE, {"text": error_msg, "panel": "chat"})
            return error_msg

    def _plan_project(self, description: str, language: str) -> dict:
        prompt = f"""
        Act as a Senior Software Architect. Plan a complete file structure for this project:
        Language: {language}
        Description: {description}
        
        CRITICAL: Return ONLY raw JSON without any markdown or conversational text. 
        Use DOUBLE QUOTES for all property names and string values.
        
        Format:
        {{
            "project_name": "snake_case_name",
            "entry_point": "main.py",
            "run_command": "python main.py",
            "files": [ {{"path": "file.py", "description": "precise logic summary"}} ],
            "dependencies": ["list", "of", "pip", "packages"]
        }}
        """
        response = self.ai.send_to_gemini(prompt)
        text = response.get("reply", str(response))
        
        try:
            return robust_json_parse(text)
        except Exception as e:
            print(f"[DevAgent] Plan Error: {e}\nRaw: {text}")
            raise ValueError(f"Failed to decode project plan from AI: {e}")

    def _write_file(self, file_info, plan, project_dir, language):
        # ULTIMATE PATH SANITIZATION: AI often fails and puts code in the path field
        raw_path = str(file_info.get("path", "file.txt"))
        
        # 1. Split by real newlines AND literal \n sequences
        parts = re.split(r'\n|\\n', raw_path)
        first_part = parts[0].strip()
        
        # 2. Extract only valid path characters (alpha-numeric, dots, slashes, underscores, hyphens)
        # We stop at the first character that isn't part of a standard filename
        path_match = re.search(r'([a-zA-Z0-9_\-\./\\]+)', first_part)
        clean_path_str = path_match.group(1) if path_match else "main_file"
        
        # 3. Final safety: remove quotes, trailing dots/slashes, and length cap
        clean_path_str = clean_path_str.replace('"', '').replace("'", "").strip(" .\\/")
        if not clean_path_str or len(clean_path_str) > 60: 
            # If it's still mess, or way too long, use a default based on language
            ext = "py" if language.lower() == "python" else "txt"
            clean_path_str = f"script_{hash(raw_path) % 1000}.{ext}"
        
        path = project_dir / clean_path_str
        path.parent.mkdir(parents=True, exist_ok=True)
        
        prompt = f"""
        As an expert {language} developer, write the code for: {clean_path_str}
        Role: {file_info.get('description', 'Code file')}
        Goal: {plan.get('project_name')}
        
        Requirements:
        1. Functional, high-quality code.
        2. Professional comments.
        3. NO markdown, NO explanation. Raw code only.
        """
        code_resp = self.ai.send_to_gemini(prompt)
        # Handle dict or string response
        if isinstance(code_resp, dict):
            code_text = code_resp.get("reply", str(code_resp))
        else:
            code_text = str(code_resp)
            
        code = self._clean_code(code_text)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(code.strip())

    def _test_run(self, cmd: str, project_dir: Path):
        """Runs the project and returns (success, output)."""
        try:
            # We run for 5 seconds to see if it crashes on startup
            process = subprocess.Popen(
                cmd, shell=True, cwd=str(project_dir),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            try:
                stdout, stderr = process.communicate(timeout=6)
                output = (stdout or "") + "\n" + (stderr or "")
            except subprocess.TimeoutExpired:
                process.kill()
                output = "Process timed out (Application remained active)."
                return True, output 

            if process.returncode != 0:
                return False, output
            return True, output
        except Exception as e:
            return False, str(e)

    def _fix_project(self, error_output: str, project_path: Path, plan: dict, language: str):
        """Asks Gemini to analyze the error and rewrite the problematic file."""
        prompt = f"""
        The project '{plan['project_name']}' failed with this error:
        ---
        {error_output[:2000]}
        ---
        Identify the faulty file and rewrite its code to fix the issue.
        Language: {language}
        
        CRITICAL: 
        1. Return ONLY the code for the FIXED file.
        2. Start with a comment identifying the file like: # FILE: path/to/file.py  OR // FILE: path/to/file.c
        """
        fix_resp = self.ai.send_to_gemini(prompt)
        if isinstance(fix_resp, dict):
            fix_text = fix_resp.get("reply", str(fix_resp))
        else:
            fix_text = str(fix_resp)
            
        code = self._clean_code(fix_text)
        
        # Robust file path extraction from the header (handles # and //)
        match = re.search(r'(?:#|//)\s*FILE:\s*([^\n\r]+)', code)
        if match:
            target_file = match.group(1).strip().split('\n')[0].strip()
            # Remove the header line from the code to avoid syntax errors
            code_lines = code.splitlines()
            if code_lines and ("FILE:" in code_lines[0]):
                code = "\n".join(code_lines[1:])
            
            path = project_path / target_file
            print(f"[DevAgent] Fixing file: {path}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(code.strip())
        else:
            # Fallback: AI didn't specify, we overwrite entry point
            entry = plan.get("entry_point", "main.py")
            path = project_path / entry
            print(f"[DevAgent] No FILE header detected. Defaulting to entry point: {path}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(code.strip())

    def _install_deps(self, deps, project_dir):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + deps, 
                           cwd=str(project_dir), capture_output=True, timeout=30)
        except: pass

    def _clean_code(self, text: str) -> str:
        text = re.sub(r'^```[a-z]*\n?', '', text, flags=re.I)
        text = re.sub(r'\n?```$', '', text)
        return text.strip()
