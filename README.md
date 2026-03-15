# 🤖 HAITOMAS ASSISTANT

**Intelligent AI Operating System Controller — Powered by Google Gemini**

HAITOMAS is a production-level AI assistant that acts as an intelligent computer operator.
It understands natural language, executes system commands, runs workflows, performs research,
writes and executes code, controls applications, sees the screen, and responds with voice.

---

## 🏗️ Architecture

```
User Input (Text/Voice)
    ↓
Intent Analyzer (instant local detection)
    ↓
Gemini AI Controller (structured JSON reasoning)
    ↓
Action Interpreter (validates response)
    ↓
Security Check (permission levels 1-3)
    ↓
Command Router → Automation Engine
    ↓
Result → UI + Voice + Memory
```

## 📦 Project Structure

```
HAITOMAS_ASSISTANT/
├── main.py                    # Entry point
├── core/                      # Processing pipeline
│   ├── assistant_loop.py      # Main orchestrator
│   ├── command_router.py      # Action dispatcher
│   ├── workflow_executor.py   # Multi-step workflows
│   ├── action_interpreter.py  # JSON validation
│   ├── code_executor.py       # Sandboxed code runner
│   └── event_bus.py           # Pub/sub events
├── brain/                     # AI reasoning
│   ├── gemini_controller.py   # Gemini API integration
│   ├── intent_analyzer.py     # Fast intent detection
│   └── context_manager.py     # Session context
├── automation/                # System control
│   ├── system_control.py      # App management
│   ├── mouse_keyboard.py      # Input automation
│   ├── browser_control.py     # Playwright browser
│   ├── file_manager.py        # File operations
│   └── window_manager.py      # Window management
├── vision/                    # Screen analysis
│   ├── screen_capture.py      # Screenshot
│   ├── screen_analyzer.py     # Context detection
│   ├── ocr_reader.py          # Text extraction
│   └── ui_element_detector.py # UI detection
├── voice/                     # Voice I/O
│   ├── speech_to_text.py      # Whisper STT
│   ├── text_to_speech.py      # pyttsx3 TTS
│   └── wake_word_detector.py  # Wake word
├── memory/                    # Persistent memory
│   ├── memory_manager.py      # Unified interface
│   ├── vector_store.py        # FAISS vectors
│   └── task_history.py        # JSON history
├── research/                  # Web research
│   ├── web_search.py          # DuckDuckGo
│   ├── web_scraper.py         # Content extraction
│   ├── content_ranker.py      # Quality scoring
│   └── summarizer.py          # AI summarization
├── security/                  # Safety system
│   ├── permission_manager.py  # 3-level permissions
│   └── safety_guard.py        # Hazard detection
├── learning/                  # User learning
│   ├── behavior_tracker.py    # Pattern tracking
│   └── task_optimizer.py      # Task caching
├── ui/                        # User interfaces
│   ├── dashboard_server.py    # FastAPI dashboard
│   ├── assistant_panel.py     # Desktop HUD
│   └── static/                # Dashboard web files
│       ├── index.html
│       ├── style.css
│       └── app.js
├── config/
│   ├── settings.py            # Settings loader
│   └── config.json            # Configuration
└── requirements.txt           # Dependencies
```

---

## 🚀 Installation

### 1. Prerequisites
- **Python 3.10+** installed
- **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 2. Install Dependencies
```bash
cd AI_Assistant
pip install -r requirements.txt
```

### 3. Install Playwright Browsers (for web automation)
```bash
playwright install chromium
```

### 4. Configure API Key
Open `config/config.json` and add your Gemini API key:
```json
{
    "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE"
}
```

### 5. Optional: Install Tesseract OCR (for screen reading)
Download from: https://github.com/UB-Mannheim/tesseract/wiki
Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

---

## ▶️ Running the Assistant

### Full Mode (Desktop HUD + Web Dashboard)
```bash
python main.py
```

### Console Mode Only
```bash
python main.py --console
```

### Dashboard Only (Web Interface)
```bash
python main.py --dashboard
```
Then open http://127.0.0.1:8500 in your browser.

### Without Web Dashboard
```bash
python main.py --no-dashboard
```

---

## 💬 Gemini Response Format

The AI always returns structured JSON:

| Type | Example |
|------|---------|
| `conversation` | `{"type": "conversation", "reply": "Hello!"}` |
| `knowledge` | `{"type": "knowledge", "topic": "AI", "reply": "..."}` |
| `command` | `{"type": "command", "command": "open_application", "parameters": {"name": "chrome"}}` |
| `workflow` | `{"type": "workflow", "goal": "...", "steps": [...]}` |
| `code_execution` | `{"type": "code_execution", "language": "python", "code": "..."}` |

---

## 🛡️ Security Levels

| Level | Actions | Behavior |
|-------|---------|----------|
| 1 - Safe | Open apps, web search, stats | Auto-execute |
| 2 - Confirm | Delete files, install software | Warns user |
| 3 - Forbidden | System32, registry, shutdown | Blocked |

---

## 🧩 Capabilities

- ✅ Natural language understanding (via Gemini)
- ✅ Open/close applications
- ✅ Web browsing and search
- ✅ Multi-step automated workflows
- ✅ Code execution in sandbox
- ✅ Screen capture and OCR
- ✅ Voice input (Whisper) and output (pyttsx3)
- ✅ Semantic memory (FAISS)
- ✅ Web research and summarization
- ✅ Real-time web dashboard
- ✅ File management
- ✅ User behavior learning
- ✅ Task optimization/caching

---

## 📄 License
Personal project. All rights reserved.
