import cv2
import os
from typing import List, Dict, Any
from core.skill import Skill
from vision.screen_capture import ScreenVision

class VisionSkill(Skill):
    """Modular Skill for Computer Vision and Object Detection (Layer 5)."""
    
    def __init__(self):
        self.vision_core = ScreenVision()
        self.model = None # Placeholder for YOLO

    @property
    def name(self) -> str:
        return "vision_skill"

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "analyze_screen",
                "description": "Capture the screen and identify what apps or content are visible.",
                "parameters": []
            },
            {
                "name": "detect_objects",
                "description": "Use the camera to detect real-world objects in the room.",
                "parameters": []
            }
        ]

    def _load_yolo(self):
        if self.model is None:
            try:
                from ultralytics import YOLO
                self.model = YOLO("yolov8n.pt")
                return True
            except:
                return False

    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        if action == "analyze_screen":
            analysis = self.vision_core.analyze_ui()
            return f"Vision Analysis complete. Context identified: {analysis['context']}. Snippet: {analysis['snippet']}"
            
        elif action == "detect_objects":
            if not self._load_yolo():
                return "Error: Vision Core (YOLO) not installed. Please install 'ultralytics'."
            
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            
            if not ret: return "Error: Camera access denied."
            
            results = self.model(frame)
            detections = []
            for r in results:
                for box in r.boxes:
                    label = self.model.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    detections.append(f"{label} ({conf:.2f})")
            
            return f"Camera Scan Complete. Detected: {', '.join(detections) if detections else 'No objects identified.'}"
        
        return None
