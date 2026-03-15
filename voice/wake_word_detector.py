"""
HAITOMAS ASSISTANT — Wake Word Detector
Optional wake word detection using keyword spotting.
"""
import threading


class WakeWordDetector:
    """Simple wake word detection (keyword-based)."""

    def __init__(self, wake_word: str = "haitomas", callback=None):
        self.wake_word = wake_word.lower()
        self.callback = callback
        self._active = False
        self._thread = None

    def start(self):
        """Start listening for wake word in background."""
        if self._active:
            return
        self._active = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print(f"[WakeWord] Listening for '{self.wake_word}'...")

    def stop(self):
        """Stop wake word detection."""
        self._active = False

    def _listen_loop(self):
        """Continuously listen for the wake word."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            mic = sr.Microphone()

            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)

            while self._active:
                try:
                    with mic as source:
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio).lower()
                    if self.wake_word in text:
                        print(f"[WakeWord] Detected: {text}")
                        if self.callback:
                            self.callback()
                except Exception:
                    continue
        except ImportError:
            print("[WakeWord] speech_recognition not installed. Wake word disabled.")
            self._active = False
        except Exception as e:
            print(f"[WakeWord] Error: {e}")
            self._active = False
