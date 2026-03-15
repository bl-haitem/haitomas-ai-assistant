"""
HAITOMAS ASSISTANT — Text to Speech
Thread-safe voice output supporting both pyttsx3 (local) and ElevenLabs (premium).
"""
import pyttsx3
import threading
import queue
import time
import requests
import io
import os
import config.settings as settings
import asyncio

if os.name == 'nt':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False


class TextToSpeech:
    """Thread-safe, queue-based text-to-speech engine."""

    def __init__(self):
        self._queue = queue.Queue()
        self._running = True
        self.available = True
        
        # Initialize pyttsx3 as fallback/secondary
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", settings.TTS_RATE)
            self._engine.setProperty("volume", settings.TTS_VOLUME)
        except Exception as e:
            print(f"[TTS] pyttsx3 Init error: {e}")
            self._engine = None

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        """Background worker that processes the speech queue."""
        while self._running:
            try:
                msg = self._queue.get(timeout=1)
                if msg is None:
                    break
                
                # Check for available engine in order: ElevenLabs (Official) -> Puter (Free ElevenLabs) -> pyttsx3 (Local)
                # Primary Engine: Edge-TTS (Best quality free/official)
                if AUDIO_LIBS_AVAILABLE:
                    self._speak_edge_tts(msg)
                elif self._engine:
                    self._speak_pyttsx3(msg)
                else:
                    print(f"[TTS] No engine available to say: {msg}")

                self._queue.task_done()
                time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTS] Worker error: {e}")

    def _speak_pyttsx3(self, text: str):
        """Speak using local pyttsx3 engine."""
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception as e:
            print(f"[TTS] pyttsx3 error: {e}")

    def _speak_elevenlabs(self, text: str):
        """Speak using official ElevenLabs API."""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
            headers = {
                "xi-api-key": settings.ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text.strip(),
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }

            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                self._play_audio(response.content)
            else:
                print(f"[TTS] ElevenLabs official error {response.status_code}. Falling back to Edge-TTS.")
                self._speak_edge_tts(text)
        except Exception as e:
            print(f"[TTS] ElevenLabs official failed: {e}")
            self._speak_edge_tts(text)

    def _speak_edge_tts(self, text: str):
        """Speak using Microsoft Edge TTS (Professional & Free)."""
        try:
            import edge_tts
            import asyncio
            
            # Detect language and choose deep, professional voices
            def detect_voice(t):
                # Strong preference for deep masculine voices as requested
                if any(ord(c) > 128 for c in t): 
                    # Arabic deep: Shakir (Egypt) or Hamed (SA)
                    return settings.EDGE_VOICES.get("ar", "ar-EG-ShakirNeural")
                
                t_low = t.lower()
                # If topic is technical/serious, use even deeper tones
                is_serious = any(w in t_low for w in ["critical", "status", "emergency", "warning", "system", "report"])
                
                if any(w in t_low for w in ["bonjour", "salut", "merci"]):
                    return settings.EDGE_VOICES.get("fr", "fr-FR-HenriNeural")
                if any(w in t_low for w in ["hallo", "danke", "guten"]):
                    return settings.EDGE_VOICES.get("de", "de-DE-ConradNeural")
                
                # Default English: Deep & Professional
                if is_serious:
                    return "en-GB-RyanNeural" # Very deep and formal
                return settings.EDGE_VOICES.get("en", "en-US-ChristopherNeural") # Deep American
            
            # Clean text from any accidental JSON strings
            import re
            text_to_speak = re.sub(r'\{.*\}', '', text).strip()
            if not text_to_speak: 
                # If everything was JSON, maybe use a generic phrase
                text_to_speak = "Executing command, Commander." if "ar" not in detect_voice(text) else "جاري التنفيذ، أيها القائد."

            voice = detect_voice(text_to_speak)
            
            async def _save_and_play():
                # Add slight rate adjustment for more "authority"
                rate = "+0%"
                pitch = "-5Hz" # Slightly lower pitch for more depth
                communicate = edge_tts.Communicate(text_to_speak, voice, rate=rate, pitch=pitch)
                temp_file = "temp_voice.mp3"
                await communicate.save(temp_file)
                
                data, samplerate = sf.read(temp_file, dtype="float32")
                sd.stop() # Stop any current sound
                sd.play(data, samplerate)
                sd.wait() # This is fine as it's in a worker thread
                
                if os.path.exists(temp_file):
                    try: os.remove(temp_file)
                    except: pass

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_save_and_play())
            loop.close()

        except Exception as e:
            print(f"[TTS] Edge-TTS failed: {e}")
            self._speak_pyttsx3(text)

    def _speak_puter(self, text: str):
        """Legacy: Puter is often 403, using Edge-TTS instead."""
        self._speak_edge_tts(text)

    def _play_audio(self, content: bytes):
        """Play raw audio bytes using sounddevice."""
        if not AUDIO_LIBS_AVAILABLE:
            return
        audio_data = io.BytesIO(content)
        data, samplerate = sf.read(audio_data, dtype="float32")
        sd.play(data, samplerate)
        sd.wait()

    def speak(self, text: str):
        """Add text to the speech queue (non-blocking)."""
        if self.available and text:
            self._queue.put(text)

    def interrupt(self):
        """Immediately stop any ongoing playback and clear the queue."""
        # Clear the queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                # self._queue.task_done() # Can cause errors if not careful
            except:
                break
        
        # Stop sounddevice immediately
        if AUDIO_LIBS_AVAILABLE:
            try:
                sd.stop()
            except:
                pass
        print("[TTS] Interrupted playback.")

    def stop(self):
        """Stop the TTS engine."""
        self._running = False
        self._queue.put(None)

    def set_voice(self, index: int = 0):
        """Change the voice by index (for pyttsx3)."""
        if self._engine:
            try:
                voices = self._engine.getProperty("voices")
                if index < len(voices):
                    self._engine.setProperty("voice", voices[index].id)
            except Exception:
                pass
