"""
HAITOMAS ASSISTANT — Screen Capture
Captures the screen using MSS for vision analysis.
"""
import os
import numpy as np


class ScreenCapture:
    """High-speed screen capture using MSS."""

    def capture(self, output_path: str = "logs/capture.png") -> str:
        """Capture the entire screen."""
        try:
            import mss
            import cv2

            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "logs", exist_ok=True)
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                cv2.imwrite(output_path, img)
            return output_path
        except Exception as e:
            return f"Capture error: {e}"

    def capture_region(self, x: int, y: int, w: int, h: int,
                       output_path: str = "logs/region.png") -> str:
        """Capture a specific region of the screen."""
        try:
            import mss
            import cv2

            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "logs", exist_ok=True)
            with mss.mss() as sct:
                monitor = {"top": y, "left": x, "width": w, "height": h}
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                cv2.imwrite(output_path, img)
            return output_path
        except Exception as e:
            return f"Region capture error: {e}"

    def get_screen_array(self) -> np.ndarray | None:
        """Return screen as numpy array for analysis."""
        try:
            import mss
            import cv2

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                img = np.array(sct.grab(monitor))
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        except Exception:
            return None
