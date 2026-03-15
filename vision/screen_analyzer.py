"""
HAITOMAS ASSISTANT — Screen Analyzer
High-level screen analysis combining capture + OCR + context detection.
"""
from vision.screen_capture import ScreenCapture
from vision.ocr_reader import OCRReader


class ScreenAnalyzer:
    """Unified screen analysis — see, read, and understand the screen."""

    def __init__(self):
        self.capture = ScreenCapture()
        self.ocr = OCRReader()

    def capture_screen(self, path: str = "") -> str:
        """Capture screenshot and return path."""
        output = path or "logs/capture.png"
        return self.capture.capture(output)

    def read_screen_text(self) -> str:
        """Read all text currently visible on screen."""
        img = self.capture.get_screen_array()
        if img is None:
            return "Could not capture screen."
        return self.ocr.read_from_array(img)

    def find_on_screen(self, text: str) -> tuple | None:
        """Find coordinates of text on screen."""
        img = self.capture.get_screen_array()
        if img is None:
            return None
        return self.ocr.find_text_location(img, text)

    def analyze_ui_context(self) -> dict:
        """Detect what application/context is currently active."""
        text = self.read_screen_text()

        context_map = {
            "Visual Studio": "VS Code (Coding)",
            "Google Chrome": "Chrome Browser",
            "Microsoft Edge": "Edge Browser",
            "File Explorer": "File Manager",
            "Settings": "System Settings",
            "Task Manager": "System Monitor",
            "Word": "Microsoft Word",
            "Excel": "Microsoft Excel",
            "Outlook": "Microsoft Outlook",
            "Discord": "Discord",
            "YouTube": "YouTube",
        }

        detected = "Desktop"
        for keyword, label in context_map.items():
            if keyword.lower() in text.lower():
                detected = label
                break

        return {
            "context": detected,
            "text_snippet": text[:300].strip(),
            "status": "active"
        }
