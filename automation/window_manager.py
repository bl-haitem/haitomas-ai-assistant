"""
HAITOMAS ASSISTANT — Window Manager
Controls window focus, positioning, and arrangement.
"""
import subprocess
import os


class WindowManager:
    """Window management for the operating system."""

    def focus_window(self, title: str) -> str:
        """Bring a window to the foreground by title."""
        if os.name != "nt":
            return "Window management only supported on Windows."
        try:
            # Use PowerShell to find and focus window
            ps_script = f'''
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class Win32 {{
                [DllImport("user32.dll")]
                public static extern bool SetForegroundWindow(IntPtr hWnd);
            }}
"@
            $proc = Get-Process | Where-Object {{$_.MainWindowTitle -like "*{title}*"}} | Select-Object -First 1
            if ($proc) {{
                [Win32]::SetForegroundWindow($proc.MainWindowHandle)
            }}
            '''
            subprocess.run(["powershell", "-Command", ps_script],
                         capture_output=True, timeout=5)
            return f"Focused window: {title}"
        except Exception as e:
            return f"Focus error: {e}"

    def minimize_window(self, title: str = "") -> str:
        """Minimize a window or all windows."""
        try:
            import pyautogui
            if title:
                self.focus_window(title)
                import time
                time.sleep(0.3)
            pyautogui.hotkey("win", "down")
            return f"Minimized: {title or 'current window'}"
        except Exception as e:
            return f"Minimize error: {e}"

    def maximize_window(self, title: str = "") -> str:
        """Maximize a window."""
        try:
            import pyautogui
            if title:
                self.focus_window(title)
                import time
                time.sleep(0.3)
            pyautogui.hotkey("win", "up")
            return f"Maximized: {title or 'current window'}"
        except Exception as e:
            return f"Maximize error: {e}"

    def list_windows(self) -> str:
        """List all open windows."""
        if os.name != "nt":
            return "Window listing only supported on Windows."
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object -Property ProcessName, MainWindowTitle | Format-Table -AutoSize"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.stdout else "No windows found."
        except Exception as e:
            return f"List windows error: {e}"

    def snap_window(self, direction: str = "left") -> str:
        """Snap current window to a side (left/right)."""
        try:
            import pyautogui
            if direction.lower() == "left":
                pyautogui.hotkey("win", "left")
            elif direction.lower() == "right":
                pyautogui.hotkey("win", "right")
            return f"Snapped window: {direction}"
        except Exception as e:
            return f"Snap error: {e}"
