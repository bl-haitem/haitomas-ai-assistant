"""
HAITOMAS ASSISTANT — System Control
Handles application lifecycle, system queries, web access, and PDF generation.
"""
import os
import subprocess
import webbrowser
import time
import json
import config.settings as settings


class SystemControl:
    """Core system automation: apps, web, media, system info, PDF."""

    def __init__(self):
        self.smart_browser = None  # Will be set by AssistantLoop
        # We don't store them as local attributes anymore to ensure we always get the latest
        self.default_apps = {
            "chrome": "chrome", "browser": "chrome",
            "notepad": "notepad", "calculator": "calc",
            "vscode": "code", "code": "code",
            "excel": "excel", "word": "winword",
            "outlook": "outlook", "explorer": "explorer",
            "paint": "mspaint", "cmd": "cmd",
            "powershell": "powershell", "terminal": "wt",
            "task manager": "taskmgr", "settings": "ms-settings:",
        }

    def open_app(self, app_name: str) -> str:
        """Open an application by name."""
        if not app_name:
            return "No application name provided."

        # Direct file/path check
        if os.path.exists(app_name):
            try:
                os.startfile(app_name)
                return f"OPENED: {app_name}"
            except Exception as e:
                return f"Path error: {e}"

        name = app_name.lower().strip()

        # Web alias check
        if name in settings.WEB_ALIASES:
            return self.web_open(settings.WEB_ALIASES[name])

        # URL detection
        if "." in name and " " not in name and not name.endswith(".exe"):
            return self.web_open(name)

        # Custom app paths
        if name in settings.APP_PATHS:
            exec_path = settings.APP_PATHS[name]
        elif name in self.default_apps:
            exec_path = self.default_apps[name]
        else:
            exec_path = self._find_executable(name)

        # SPECIAL FIX FOR VS CODE ON WINDOWS
        if (name == "code" or name == "vscode") and os.name == "nt":
            # Check common paths
            check_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft VS Code\bin\code.cmd"),
                "code"
            ]
            for p in check_paths:
                if os.path.exists(p) or p == "code":
                    exec_path = p
                    if os.path.exists(p): break

        try:
            if os.name == "nt":
                # Use shell=True for .cmd files like 'code'
                subprocess.Popen(f'start "" "{exec_path}"', shell=True)
            else:
                subprocess.Popen([exec_path])
            return f"LAUNCHED: {app_name.upper()}"
        except Exception as e:
            return f"Could not open {app_name}: {e}"

    def close_app(self, app_name: str) -> str:
        """Close a running application."""
        name = app_name.lower().strip()
        process_map = {
            "notepad": "notepad.exe", "chrome": "chrome.exe",
            "vscode": "Code.exe", "code": "Code.exe",
            "calculator": "CalculatorApp.exe", "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE", "outlook": "OUTLOOK.EXE",
            "explorer": "explorer.exe", "browser": "chrome.exe",
        }

        target = process_map.get(name, name)
        if not target.endswith(".exe") and os.name == "nt":
            target += ".exe"

        try:
            if os.name == "nt":
                subprocess.run(f"taskkill /F /IM {target}", shell=True,
                             check=True, capture_output=True)
            else:
                subprocess.run(["pkill", "-f", target], check=True)
            return f"TERMINATED: {app_name.upper()}"
        except Exception:
            return f"Could not close {app_name} (may not be running)."

    def web_search(self, query: str) -> str:
        """Open a web search in the default browser."""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching for: {query}"

    def web_open(self, url: str) -> str:
        """Open a URL or search in the browser."""
        # Check if it's a domain or just keywords
        if not url.startswith("http"):
            if "." not in url and " " in url:
                return self.web_search(url)
            url = f"https://{url}"
        webbrowser.open(url)
        return f"Opening: {url}"

    def play_youtube_video(self, query: str) -> str:
        """Search and play a YouTube video using SmartBrowser."""
        if self.smart_browser:
            return self.smart_browser.play_youtube_video(query)
        # Fallback: just open the search page
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        return f"Launching YouTube for: {query}"

    def media_control(self, command: str) -> str:
        """Control media playback and system volume."""
        try:
            import pyautogui
            # Keyboard mapping
            mapping = {
                "play": "playpause", "pause": "playpause",
                "next": "nexttrack", "prev": "prevtrack",
                "volume_up": "volumeup", "volume_down": "volumedown",
                "mute": "volumemute"
            }
            key = mapping.get(command.lower())
            if key:
                pyautogui.press(key)
                return f"🔊 System Media: {command}"
            
            # Numeric volume control
            if "volume_" in command and any(d.isdigit() for d in command):
                # Placeholder for direct volume setting if needed
                pass
                
            return f"Unknown media command: {command}"
        except Exception as e:
            return f"Media control error: {e}"

    def send_whatsapp_native(self, contact: str, message: str) -> str:
        """Send message via WhatsApp Desktop app (Native)."""
        import pyautogui
        try:
            # 1. Open App
            self.open_app("WhatsApp")
            time.sleep(2)
            # 2. Search contact (Ctrl+F is universal for search in desktop apps)
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.5)
            pyautogui.write(contact, interval=0.05)
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(0.5)
            # 3. Type and Send
            pyautogui.write(message, interval=0.03)
            pyautogui.press("enter")
            return f"✅ Native WhatsApp: Message sent to {contact}."
        except Exception as e:
            return f"Native WhatsApp Error: {e}"

    def send_telegram_native(self, contact: str, message: str) -> str:
        """Send message via Telegram Desktop app."""
        import pyautogui
        try:
            self.open_app("Telegram")
            time.sleep(2)
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.5)
            pyautogui.write(contact, interval=0.05)
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(0.5)
            pyautogui.write(message, interval=0.03)
            pyautogui.press("enter")
            return f"✅ Native Telegram: Message sent to {contact}."
        except Exception as e:
            return f"Native Telegram Error: {e}"

    def send_email(self, recipient: str, subject: str = "", body: str = "") -> str:
        """Send an email using Gmail's compose window with pre-filled fields."""
        import urllib.parse
        from core.event_bus import event_bus, EVENT_SPEAK
        from core.voice_library import get_phrase
        
        # Feedback
        lang = "ar" if any(ord(c) > 128 for c in (recipient + subject + body)) else "en"
        event_bus.publish(EVENT_SPEAK, {"text": get_phrase("email_prep", lang)})

        # URL Encoding
        safe_recipient = urllib.parse.quote(recipient)
        safe_subject = urllib.parse.quote(subject)
        safe_body = urllib.parse.quote(body)

        # Gmail Compose URL
        url = f"https://mail.google.com/mail/?view=cm&fs=1&to={safe_recipient}&su={safe_subject}&body={safe_body}"
        webbrowser.open(url)
        
        return f"Email compose window opened for {recipient}."

    def open_overleaf_with_latex(self, latex_content: str, project_name: str = "Academic_Paper") -> str:
        """Saves LaTeX content locally and opens Overleaf for the user."""
        try:
            filename = project_name.replace(" ", "_").lower()
            out_dir = "output/latex"
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, f"{filename}.tex")
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(latex_content)
            
            # Open Overleaf and the local folder
            webbrowser.open("https://www.overleaf.com/project")
            os.startfile(os.path.abspath(out_dir))
            
            return f"LaTeX file created at {path}. I've opened Overleaf and the local folder for you."
        except Exception as e:
            return f"LaTeX error: {e}"

    def system_query(self, query: str) -> str:
        """Query system information."""
        try:
            import psutil
            q = query.lower()

            if "cpu" in q:
                return f"CPU usage: {psutil.cpu_percent(interval=1)}%"
            elif "battery" in q:
                battery = psutil.sensors_battery()
                if battery:
                    plugged = "plugged in" if battery.power_plugged else "on battery"
                    return f"Battery: {battery.percent}% ({plugged})"
                return "No battery detected."
            elif "ram" in q or "memory" in q:
                mem = psutil.virtual_memory()
                used_gb = mem.used / (1024**3)
                total_gb = mem.total / (1024**3)
                return f"RAM: {mem.percent}% used ({used_gb:.1f}/{total_gb:.1f} GB)"
            elif "disk" in q:
                disk = psutil.disk_usage("/")
                used_gb = disk.used / (1024**3)
                total_gb = disk.total / (1024**3)
                return f"Disk: {disk.percent}% used ({used_gb:.1f}/{total_gb:.1f} GB)"
            else:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                return f"System: CPU {cpu}% | RAM {mem.percent}% | Cores: {psutil.cpu_count()}"
        except Exception as e:
            return f"System query error: {e}"

    def generate_pdf(self, title: str, content: str, filename: str = "report") -> str:
        """Generate a PDF report."""
        try:
            from fpdf import FPDF
            from fpdf.enums import XPos, YPos

            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, str(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.ln(5)

            pdf.set_font("helvetica", size=10)
            pdf.cell(0, 10, f"Generated by HAITOMAS — {time.ctime()}",
                    new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
            pdf.ln(10)

            pdf.set_font("helvetica", size=11)
            pdf.multi_cell(0, 8, str(content))

            out_path = f"output/{filename}.pdf"
            os.makedirs("output", exist_ok=True)
            pdf.output(out_path)
            return f"PDF generated: {out_path}"
        except Exception as e:
            return f"PDF error: {e}"

    def _find_executable(self, name: str) -> str:
        """Search for an executable in common Windows locations."""
        search_dirs = [
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
            os.path.join(os.environ.get("LocalAppData", ""), "Programs"),
        ]

        known_paths = {
            "chrome": r"Google\Chrome\Application\chrome.exe",
            "edge": r"Microsoft\Edge\Application\msedge.exe",
            "brave": r"BraveSoftware\Brave-Browser\Application\brave.exe",
            "outlook": r"Microsoft Office\root\Office16\OUTLOOK.EXE",
            "word": r"Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"Microsoft Office\root\Office16\EXCEL.EXE",
            "powerpoint": r"Microsoft Office\root\Office16\POWERPNT.EXE",
            "telegram": r"Telegram Desktop\Telegram.exe",
            "whatsapp": r"WhatsApp\WhatsApp.exe",
            "discord": r"Discord\Update.exe --processStart Discord.exe"
        }

        if name in known_paths:
            for d in search_dirs:
                full = os.path.join(d, known_paths[name])
                if os.path.exists(full):
                    return full

        # Try PATH
        try:
            return subprocess.check_output(
                f"where {name}", shell=True
            ).decode().split("\n")[0].strip()
        except Exception:
            pass

        return name