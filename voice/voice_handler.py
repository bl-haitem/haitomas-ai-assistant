import pyttsx3
import threading
import queue
import time

class VoiceHandler:
    """Thread-safe, queue-based voice manager for haitomas."""
    def __init__(self):
        self.queue = queue.Queue()
        self.engine = pyttsx3.init()
        # High-performance speech parameters
        self.engine.setProperty('rate', 185)
        self.engine.setProperty('volume', 0.9)
        
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while True:
            msg = self.queue.get()
            if msg is None: break
            try:
                self.engine.say(msg)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[VoiceError] {e}")
            self.queue.task_done()
            time.sleep(0.1)

    def speak(self, text):
        """Asynchronous, non-blocking speak command."""
        self.queue.put(text)
