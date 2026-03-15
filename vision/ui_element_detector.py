"""
HAITOMAS ASSISTANT — UI Element Detector
Detects buttons, input fields, and other UI elements on screen using OpenCV.
"""
import numpy as np


class UIElementDetector:
    """Detect UI components on the screen using computer vision."""

    def detect_buttons(self, img_array: np.ndarray) -> list:
        """Detect button-like rectangles on screen."""
        try:
            import cv2

            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            buttons = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 50000:  # Typical button size range
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect = w / max(h, 1)
                    if 1.5 < aspect < 8.0:  # Buttons are wider than tall
                        buttons.append({
                            "x": x, "y": y, "w": w, "h": h,
                            "center": (x + w // 2, y + h // 2)
                        })

            return buttons[:20]  # Limit results
        except Exception as e:
            print(f"[UIDetector] Error: {e}")
            return []

    def detect_text_fields(self, img_array: np.ndarray) -> list:
        """Detect input field-like rectangles on screen."""
        try:
            import cv2

            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            fields = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 2000 < area < 100000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect = w / max(h, 1)
                    if aspect > 3.0 and h < 60:  # Text fields are long and thin
                        fields.append({
                            "x": x, "y": y, "w": w, "h": h,
                            "center": (x + w // 2, y + h // 2)
                        })

            return fields[:15]
        except Exception as e:
            print(f"[UIDetector] Error: {e}")
            return []
