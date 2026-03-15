"""
HAITOMAS ASSISTANT — Code Executor
Sandboxed code execution for Python and shell commands.
"""
import subprocess
import sys
import os
import tempfile
from security.safety_guard import SafetyGuard


class CodeExecutor:
    """Safe code execution in isolated sandbox."""

    def __init__(self):
        self.guard = SafetyGuard()
        self.output_dir = os.path.join(tempfile.gettempdir(), "haitomas_sandbox")
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(self, code: str, language: str = "python") -> str:
        """Execute code safely and return output."""
        # Safety check
        is_safe, message = self.guard.validate_code(code)
        if not is_safe:
            return f"⛔ BLOCKED: {message}"

        if language.lower() == "python":
            return self._run_python(code)
        elif language.lower() in ["shell", "cmd", "powershell"]:
            return self._run_shell(code)
        else:
            return f"Unsupported language: {language}"

    def _run_python(self, code: str) -> str:
        """Execute Python code in a subprocess."""
        try:
            # Write code to temp file
            script_path = os.path.join(self.output_dir, "sandbox_script.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Run in subprocess with timeout
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.output_dir
            )

            output = result.stdout.strip()
            errors = result.stderr.strip()

            if result.returncode == 0:
                return output or "Code executed successfully (no output)."
            else:
                return f"Error:\n{errors}" if errors else f"Exit code: {result.returncode}"

        except subprocess.TimeoutExpired:
            return "⏱ Code execution timed out (30s limit)."
        except Exception as e:
            return f"Execution error: {e}"

    def _run_shell(self, command: str) -> str:
        """Execute a shell/CMD command."""
        try:
            # Extra safety check for shell commands
            dangerous = ["format", "del /f", "rd /s", "shutdown", "diskpart"]
            if any(d in command.lower() for d in dangerous):
                return f"⛔ BLOCKED: Dangerous shell command detected."

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout.strip()
            errors = result.stderr.strip()

            if result.returncode == 0:
                return output or "Command executed successfully."
            else:
                return f"Error:\n{errors}" if errors else f"Exit code: {result.returncode}"

        except subprocess.TimeoutExpired:
            return "⏱ Command timed out."
        except Exception as e:
            return f"Shell error: {e}"
