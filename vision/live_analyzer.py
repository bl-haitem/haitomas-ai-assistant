"""
HAITOMAS ASSISTANT — Live Analyzer (Gemini Live Vision)
=====================================================
Real-time screen and camera analysis using the Gemini 2.0/2.5 Flash Live API.
Features: Continuous screen capture, audio feedback, and visual understanding.
Credits: Inspired by Mark-XXX screen_processor.
"""
import asyncio
import base64
import io
import json
import os
import sys
import time
import threading
import cv2
import mss
import pyaudio
import PIL.Image
from pathlib import Path
from google import genai
from google.genai import types
from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK

# Configuration
LIVE_MODEL = "models/gemini-2.0-flash-exp" # Or gemini-2.5-flash-native-audio-preview
SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
IMG_MAX_W = 640
IMG_MAX_H = 360
JPEG_Q = 55

class LiveAnalyzer:
    """
    Advanced vision system that analyzes the screen and camera in real-time.
    Supports a 'Live' perspective mode.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        self.loop = None
        self.thread = None
        self.is_active = False
        self.out_queue = None
        self.audio_out = None # Will be initialized in _run_async_loop
        self.player_stream = None
        
        # System Prompt for Vision JARVIS mode
        self.system_prompt = (
            "You are HAITOMAS (Elite AI Commander). "
            "You are observing the user's screen or camera in real-time. "
            "Analyze visuals with technical precision and elite intelligence. "
            "Be concise, smart, and direct. Use a commander tone. "
            "Respond in 1-2 short sentences maximum. Speed is critical."
        )

    def start_live_session(self):
        """Starts the asynchronous background loop for the live session."""
        if self.is_active: return
        self.is_active = True
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()
        print("[LiveVision] 🚀 Live session thread started.")

    def _run_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._main_loop())

    async def _main_loop(self):
        self.out_queue = asyncio.Queue(maxsize=10)
        
        # Initialize Audio here to avoid startup conflicts
        if not self.audio_out:
            self.audio_out = pyaudio.PyAudio()

        client = genai.Client(api_key=self.api_key, http_options={"api_version": "v1beta"})
        
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=self.system_prompt,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon"))
            )
        )

        while self.is_active:
            try:
                print("[LiveVision] 🔌 Connecting to Gemini Live API...")
                async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
                    self.session = session
                    print("[LiveVision] ✅ Connected.")
                    
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(self._send_loop())
                        tg.create_task(self._receive_loop())
                        tg.create_task(self._play_loop())
            except Exception as e:
                print(f"[LiveVision] ⚠️ Connection error: {e}. Reconnecting in 3s...")
                await asyncio.sleep(3)

    async def _send_loop(self):
        """Monitors the queue and sends images to Gemini."""
        while self.is_active:
            img_bytes, mime, text = await self.out_queue.get()
            if self.session:
                try:
                    b64_data = base64.b64encode(img_bytes).decode("utf-8")
                    await self.session.send_client_content(
                        turns={
                            "parts": [
                                {"inline_data": {"mime_type": mime, "data": b64_data}},
                                {"text": text}
                            ]
                        },
                        turn_complete=True
                    )
                except Exception as e:
                    print(f"[LiveVision] Send failed: {e}")

    async def _receive_loop(self):
        """Receives audio and transcripts from Gemini."""
        while self.is_active:
            try:
                async for response in self.session.receive():
                    if response.data:
                        # Feed audio to the player loop
                        event_bus.publish("live_audio_chunk", {"data": response.data})
                    
                    # Log transcription for UI
                    sc = response.server_content
                    if sc and sc.output_transcription:
                        text = sc.output_transcription.text
                        if text:
                            event_bus.publish(EVENT_UI_UPDATE, {"text": f"👁️ JARVIS: {text}", "panel": "chat"})
            except Exception as e:
                print(f"[LiveVision] Receive error: {e}")
                break

    async def _play_loop(self):
        """Plays the received audio chunks. Lazily opens stream to avoid device lock."""
        audio_queue = asyncio.Queue()
        event_bus.subscribe("live_audio_chunk", lambda d: asyncio.run_coroutine_threadsafe(audio_queue.put(d['data']), self.loop))

        try:
            while self.is_active:
                chunk = await audio_queue.get()
                
                # Open stream only when we have actual audio to play
                if not self.player_stream:
                    print("[LiveVision] 🔊 Opening audio output stream...")
                    self.player_stream = self.audio_out.open(
                        format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, output=True
                    )
                
                await asyncio.to_thread(self.player_stream.write, chunk)
        except Exception as e:
            print(f"[LiveVision] Play loop error: {e}")
        finally:
            if self.player_stream:
                self.player_stream.close()
                self.player_stream = None

    def analyze_now(self, user_text: str, source: str = "screen"):
        """Trigger a visual analysis of the current screen/camera."""
        if not self.is_active:
            self.start_live_session()
            time.sleep(2) # Brief wait for connection

        try:
            if source == "camera":
                img_bytes = self._capture_camera()
            else:
                img_bytes = self._capture_screen()
                
            asyncio.run_coroutine_threadsafe(
                self.out_queue.put((img_bytes, "image/jpeg", user_text)),
                self.loop
            )
        except Exception as e:
            print(f"[LiveVision] Analysis trigger failed: {e}")

    def _capture_screen(self) -> bytes:
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[1])
            img_raw = PIL.Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            img_raw.thumbnail((IMG_MAX_W, IMG_MAX_H), PIL.Image.Resampling.BILINEAR)
            buf = io.BytesIO()
            img_raw.save(buf, format="JPEG", quality=JPEG_Q)
            return buf.getvalue()

    def _capture_camera(self) -> bytes:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret: raise RuntimeError("Camera failed.")
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(rgb_frame)
        img.thumbnail((IMG_MAX_W, IMG_MAX_H), PIL.Image.Resampling.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_Q)
        return buf.getvalue()

    def stop(self):
        self.is_active = False
        if self.session:
            # We would need to properly close the session here
            pass
