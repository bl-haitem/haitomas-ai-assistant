"""
HAITOMAS ASSISTANT — Centralized Settings Manager
Loads config.json and provides typed access to all values.
"""
import json
import os

# Project root directory (one level up from config/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "config.json")


def _load_config() -> dict:
    """Load configuration from disk."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Settings] config.json not found at {CONFIG_PATH}, using defaults.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[Settings] config.json parse error: {e}")
        return {}


def save_config(cfg: dict):
    """Persist configuration to disk."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Singleton-style config dict — imported by other modules
# ---------------------------------------------------------------------------
_cfg = _load_config()

# Gemini
GEMINI_API_KEY: str = _cfg.get("gemini_api_key", "")
GEMINI_MODEL: str = _cfg.get("gemini_model", "gemini-2.0-flash")
GEMINI_LIVE_MODEL: str = _cfg.get("gemini_live_model", "models/gemini-2.0-flash-exp")

# OpenRouter
OPENROUTER_API_KEY: str = _cfg.get("openrouter_api_key", "")
OPENROUTER_MODEL: str = _cfg.get("openrouter_model", "google/gemini-2.0-flash-exp:free")

# Personas
ACTIVE_PERSONA: str = _cfg.get("active_persona", "Assistant")
PERSONAS: dict = _cfg.get("personas", {
    "Assistant": {
        "name": "haitomas",
        "mentality": "Professional, efficient, and concise computer controller.",
        "voice_index": 0
    }
})

# Web aliases
WEB_ALIASES: dict = _cfg.get("web_aliases", {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chat.openai.com",
    "github": "https://www.github.com",
    "whatsapp": "https://web.whatsapp.com"
})

# App paths (user-configurable overrides)
APP_PATHS: dict = _cfg.get("app_paths", {})

# Tesseract OCR path
TESSERACT_PATH: str = _cfg.get("tesseract_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Voice
TTS_ENGINE: str = _cfg.get("tts_engine", "pyttsx3") # Options: pyttsx3, elevenlabs
TTS_RATE: int = _cfg.get("tts_rate", 185)
TTS_VOLUME: float = _cfg.get("tts_volume", 0.9)
ELEVENLABS_API_KEY: str = _cfg.get("elevenlabs_api_key", "")
ELEVENLABS_VOICE_ID: str = _cfg.get("elevenlabs_voice_id", "JBFqnCBsd6RMkjVDRZzb")

# Edge TTS Voices
EDGE_VOICES: dict = _cfg.get("edge_voices", {
    "ar": "ar-EG-ShakirNeural",
    "en": "en-US-GuyNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural"
})

# Dashboard
DASHBOARD_HOST: str = _cfg.get("dashboard_host", "127.0.0.1")
DASHBOARD_PORT: int = _cfg.get("dashboard_port", 8500)

# Security
SAFETY_ENABLED: bool = _cfg.get("safety_enabled", True)

# Memory
MEMORY_DIR: str = os.path.join(PROJECT_ROOT, "memory", "data")
HISTORY_FILE: str = os.path.join(PROJECT_ROOT, "memory", "task_history.json")


def get_persona_prompt() -> str:
    """Return the mentality string for the currently active persona."""
    persona = PERSONAS.get(ACTIVE_PERSONA, {})
    return persona.get("mentality", "Professional AI assistant")


def reload():
    """Re-read config from disk (useful after user edits config.json)."""
    global _cfg, GEMINI_API_KEY, GEMINI_MODEL, OPENROUTER_API_KEY, OPENROUTER_MODEL
    global ACTIVE_PERSONA, PERSONAS, WEB_ALIASES, APP_PATHS
    global TTS_ENGINE, TTS_RATE, TTS_VOLUME, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
    global EDGE_VOICES
    _cfg = _load_config()
    GEMINI_API_KEY = _cfg.get("gemini_api_key", "")
    GEMINI_MODEL = _cfg.get("gemini_model", "gemini-2.0-flash")
    OPENROUTER_API_KEY = _cfg.get("openrouter_api_key", "")
    OPENROUTER_MODEL = _cfg.get("openrouter_model", "google/gemini-2.0-flash-exp:free")
    ACTIVE_PERSONA = _cfg.get("active_persona", "Assistant")
    PERSONAS = _cfg.get("personas", PERSONAS)
    WEB_ALIASES = _cfg.get("web_aliases", WEB_ALIASES)
    APP_PATHS = _cfg.get("app_paths", APP_PATHS)
    TTS_ENGINE = _cfg.get("tts_engine", "pyttsx3")
    TTS_RATE = _cfg.get("tts_rate", 185)
    TTS_VOLUME = _cfg.get("tts_volume", 0.9)
    ELEVENLABS_API_KEY = _cfg.get("elevenlabs_api_key", "")
    ELEVENLABS_VOICE_ID = _cfg.get("elevenlabs_voice_id", "JBFqnCBsd6RMkjVDRZzb")
    EDGE_VOICES = _cfg.get("edge_voices", EDGE_VOICES)
