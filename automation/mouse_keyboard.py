"""
HAITOMAS ASSISTANT — Mouse & Keyboard Control
Low-level input automation using pyautogui.
"""
import pyautogui
import time

# Safety: moving mouse to corner will abort
pyautogui.FAILSAFE = True


class MouseKeyboard:
    """Human-like mouse and keyboard control."""

    def click(self, x: int = None, y: int = None, button: str = "left") -> str:
        """Click at coordinates or current position."""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
                return f"Clicked at ({x}, {y})"
            else:
                pyautogui.click(button=button)
                return "Clicked at current position."
        except Exception as e:
            return f"Click error: {e}"

    def double_click(self, x: int = None, y: int = None) -> str:
        """Double-click."""
        try:
            if x and y:
                pyautogui.doubleClick(x, y)
            else:
                pyautogui.doubleClick()
            return "Double-clicked."
        except Exception as e:
            return f"Double-click error: {e}"

    def right_click(self, x: int = None, y: int = None) -> str:
        """Right-click."""
        return self.click(x, y, button="right")

    def type_text(self, text: str, interval: float = 0.04) -> str:
        """Type text character by character."""
        try:
            pyautogui.write(str(text), interval=interval)
            return f"Typed: {text}"
        except Exception as e:
            return f"Type error: {e}"

    def press_key(self, key: str) -> str:
        """Press a single key."""
        try:
            pyautogui.press(str(key).lower())
            return f"Pressed: {key}"
        except Exception as e:
            return f"Key press error: {e}"

    def hotkey(self, keys: str) -> str:
        """Execute a keyboard shortcut (e.g., 'ctrl+c')."""
        try:
            key_list = [k.strip() for k in str(keys).replace(" ", "").split("+")]
            pyautogui.hotkey(*key_list)
            return f"Hotkey: {keys}"
        except Exception as e:
            return f"Hotkey error: {e}"

    def move_to(self, x: int, y: int, duration: float = 0.5) -> str:
        """Move mouse to coordinates."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return f"Moved to ({x}, {y})"
        except Exception as e:
            return f"Move error: {e}"

    def scroll(self, amount: int = 3) -> str:
        """Scroll up (positive) or down (negative)."""
        try:
            pyautogui.scroll(amount)
            direction = "up" if amount > 0 else "down"
            return f"Scrolled {direction} by {abs(amount)}"
        except Exception as e:
            return f"Scroll error: {e}"

    def drag_to(self, x: int, y: int, duration: float = 0.5) -> str:
        """Drag from current position to target."""
        try:
            pyautogui.dragTo(x, y, duration=duration)
            return f"Dragged to ({x}, {y})"
        except Exception as e:
            return f"Drag error: {e}"

    def get_position(self) -> tuple:
        """Get current mouse position."""
        return pyautogui.position()

    def wait(self, seconds: float) -> str:
        """Wait for specified seconds."""
        time.sleep(seconds)
        return f"Waited {seconds}s"
