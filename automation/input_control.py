import pyautogui
import time

class InputControl:
    def __init__(self):
        pyautogui.FAILSAFE = True

    def click(self, position=None):
        """Clicks at position (x, y) or current mouse position."""
        if position:
            pyautogui.click(position[0], position[1])
        else:
            pyautogui.click()

    def type_text(self, text):
        """Types text with a slight delay."""
        pyautogui.write(text, interval=0.05)
        pyautogui.press('enter')

    def press_key(self, key):
        """Presses a single key."""
        pyautogui.press(key)

    def execute_action(self, action_obj):
        action = action_obj.get("action")
        param = action_obj.get("param")

        try:
            if action == "click":
                self.click()
                return "Clicked."
            elif action == "type":
                self.type_text(str(param))
                return f"Typed: {param}"
            elif action == "press":
                self.press_key(str(param))
                return f"Pressed: {param}"
            elif action == "hotkey":
                keys = str(param).replace(" ", "").split("+")
                pyautogui.hotkey(*keys)
                return f"Hotkey: {param}"
            elif action == "wait":
                time.sleep(float(param))
                return f"Waited {param}s"
            elif action == "move":
                coords = param if isinstance(param, list) else [500, 500]
                pyautogui.moveTo(coords[0], coords[1], duration=0.5)
                return f"Moved to {coords}"
            
            return f"Unknown input action: {action}"
        except Exception as e:
            return f"Input Error: {str(e)}"