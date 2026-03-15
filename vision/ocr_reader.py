"""
HAITOMAS ASSISTANT — OCR Reader
Extracts text from the screen using Tesseract OCR.
"""
import os
from config.settings import TESSERACT_PATH


class OCRReader:
    """Tesseract-based Optical Character Recognition."""

    def __init__(self):
        try:
            import pytesseract
            if os.path.exists(TESSERACT_PATH):
                pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
            self.available = True
        except ImportError:
            self.available = False
            print("[OCR] pytesseract not available.")

    def read_from_image(self, image_path: str, lang: str = "eng") -> str:
        """Extract text from an image file."""
        if not self.available:
            return "OCR not available."
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            return pytesseract.image_to_string(img, lang=lang)
        except Exception as e:
            return f"OCR error: {e}"

    def read_from_array(self, img_array, lang: str = "eng+ara") -> str:
        """Extract text from a numpy array (screen capture)."""
        if not self.available:
            return "OCR not available."
        try:
            import pytesseract
            import cv2
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            return pytesseract.image_to_string(gray, lang=lang)
        except Exception as e:
            return f"OCR error: {e}"

    def find_text_location(self, img_array, target_text: str) -> tuple | None:
        """Find coordinates of specific text on screen."""
        if not self.available:
            return None
        try:
            import pytesseract
            import cv2
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            for i in range(len(data["text"])):
                if target_text.lower() in data["text"][i].lower():
                    x = data["left"][i] + data["width"][i] // 2
                    y = data["top"][i] + data["height"][i] // 2
                    return (x, y)
        except Exception:
            pass
        return None
