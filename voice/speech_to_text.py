"""
HAITOMAS ASSISTANT — Speech to Text
Uses OpenAI Whisper for accurate voice recognition.
"""
import sys
import os
import numpy as np
import tempfile


class SpeechToText:
    """Whisper-based speech recognition."""

    def __init__(self, model_size: str = "base"):
        self.model = None
        self.model_size = model_size

    def _load_model(self):
        """Lazy-load Whisper model."""
        if self.model is None:
            try:
                import whisper
                print(f"[STT] Loading Whisper model ({self.model_size})...")
                self.model = whisper.load_model(self.model_size)
                print("[STT] Whisper ready.")
            except Exception as e:
                print(f"[STT] Whisper load error: {e}")

    def record_and_transcribe(self, max_duration: int = 10, sample_rate: int = 16000) -> str:
        """Record audio and stop automatically when silence is detected."""
        try:
            import sounddevice as sd
            from scipy.io.wavfile import write as wav_write
            from core.event_bus import event_bus, EVENT_UI_UPDATE

            self._load_model()
            if self.model is None:
                return ""

            event_bus.publish(EVENT_UI_UPDATE, {"text": "🎙️ Listening... Speak now.", "panel": "chat"})
            print(f"[STT] Recording (max {max_duration}s)...")
            
            # Record in small chunks to detect silence
            chunk_duration = 0.5
            num_chunks = int(max_duration / chunk_duration)
            recorded_chunks = []
            
            silence_threshold = 0.005 # More sensitive
            silent_chunks = 0
            max_silent_chunks = 3 # 1.5 seconds of silence
            
            for i in range(num_chunks):
                # Update UI periodically to show activity
                if i % 2 == 0:
                    event_bus.publish(EVENT_UI_UPDATE, {"text": f"🎙️ Listening... Voice Active", "panel": "chat"})
                
                chunk = sd.rec(int(chunk_duration * sample_rate), samplerate=sample_rate,
                               channels=1, dtype="float32")
                sd.wait()
                recorded_chunks.append(chunk)
                
                # Simple energy-based silence detection
                energy = np.sqrt(np.mean(chunk**2))
                if energy < silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                
                if silent_chunks >= max_silent_chunks:
                    print("[STT] Silence detected. Stopping.")
                    break

            audio = np.concatenate(recorded_chunks, axis=0)
            event_bus.publish(EVENT_UI_UPDATE, {"text": "🧠 Transcribing your request...", "panel": "chat"})

            # Save to temp file
            temp_path = os.path.join(tempfile.gettempdir(), "haitomas_voice.wav")
            wav_write(temp_path, sample_rate, (audio * 32767).astype(np.int16))

            # Transcribe (auto-detect language)
            result = self.model.transcribe(temp_path)
            text = result.get("text", "").strip()
            print(f"[STT] Transcribed: {text}")
            
            if text:
                event_bus.publish(EVENT_UI_UPDATE, {"text": f"🗣️ Heard: {text}", "panel": "chat"})
            
            return text

        except Exception as e:
            print(f"[STT] Error: {e}")
            return ""

    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe an audio file."""
        try:
            self._load_model()
            if self.model is None:
                return ""
            result = self.model.transcribe(audio_path)
            return result.get("text", "").strip()
        except Exception as e:
            return f"Transcription error: {e}"


# CLI mode for subprocess calls
if __name__ == "__main__":
    stt = SpeechToText()
    text = stt.record_and_transcribe()
    if text:
        print(f"RESULT_TEXT:{text}")
    else:
        print("RESULT_TEXT:")