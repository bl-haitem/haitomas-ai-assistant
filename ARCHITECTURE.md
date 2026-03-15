# HAITOMAS ASSISTANT — Architecture Document

## System Overview
HAITOMAS is an intelligent AI operating assistant that uses Google Gemini API
as its primary reasoning engine. It can control the computer, execute commands,
perform research, run code, and interact through voice — behaving like an
intelligent human operator.

## Execution Pipeline
```
User Input (Text / Voice)
    ↓
Assistant Core (assistant_loop.py)
    ↓
Send message to Gemini API (gemini_controller.py)
    ↓
Gemini decides request type & returns structured JSON
    ↓
Assistant parses JSON (action_interpreter.py)
    ↓
Command Router dispatches to subsystems (command_router.py)
    ↓
Automation Engine executes commands
    ↓
Result returned to user (UI + Voice)
    ↓
Memory updated (memory_manager.py)
```

## Gemini Response Types
| Type             | Purpose                                |
|------------------|----------------------------------------|
| conversation     | Natural language replies                |
| knowledge        | Factual answers with sources            |
| command          | Single system command                   |
| workflow         | Multi-step automated task               |
| code_execution   | Run Python/shell code in sandbox        |
| browser_interaction | Human-like web interaction (click/type) |

## Project Structure
```
HAITOMAS_ASSISTANT/
│
├── main.py                      # Entry point
│
├── core/
│   ├── assistant_loop.py        # Main processing loop
│   ├── command_router.py        # Routes parsed JSON to subsystems
│   ├── workflow_executor.py     # Executes multi-step workflows
│   ├── action_interpreter.py    # Parses Gemini JSON responses
│   └── event_bus.py             # Pub/sub event system
│
├── brain/
│   ├── gemini_controller.py     # Gemini API integration
│   ├── intent_analyzer.py       # Fast local intent detection
│   └── context_manager.py       # Conversation + memory context
│
├── automation/
│   ├── system_control.py        # App launch, close, system queries
│   ├── mouse_keyboard.py        # pyautogui input control
│   ├── browser_control.py       # Basic browser automation
│   ├── smart_browser.py         # Human-like web interaction (Playwright)
│   ├── file_manager.py          # File/folder operations
│   └── window_manager.py        # Window focus, resize, arrange
│
├── vision/
│   ├── screen_capture.py        # MSS screen capture
│   ├── screen_analyzer.py       # CV-based UI analysis
│   ├── ocr_reader.py            # Tesseract OCR
│   └── ui_element_detector.py   # Button/field detection
│
├── voice/
│   ├── speech_to_text.py        # Whisper STT
│   ├── text_to_speech.py        # pyttsx3 TTS
│   └── wake_word_detector.py    # Optional wake word
│
├── memory/
│   ├── memory_manager.py        # Unified memory interface
│   ├── vector_store.py          # FAISS vector storage
│   └── task_history.py          # JSON task log
│
├── research/
│   ├── web_search.py            # DuckDuckGo search
│   ├── web_scraper.py           # Trafilatura + BS4 scraping
│   ├── content_ranker.py        # Source quality ranking
│   └── summarizer.py            # AI-powered summarization
│
├── security/
│   ├── permission_manager.py    # Permission levels 1-3
│   └── safety_guard.py          # Dangerous action detection
│
├── learning/
│   ├── behavior_tracker.py      # User pattern tracking
│   └── task_optimizer.py        # Optimize repeat tasks
│
├── ui/
│   ├── dashboard_server.py      # FastAPI + WebSocket server
│   ├── static/                  # Dashboard HTML/CSS/JS
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   └── assistant_panel.py       # Desktop HUD (PyQt6/Tkinter)
│
├── config/
│   ├── settings.py              # Centralized settings loader
│   └── config.json              # User configuration
│
└── requirements.txt             # All dependencies
```

## Security Levels
| Level | Description              | Examples                      |
|-------|--------------------------|-------------------------------|
| 1     | Safe (auto-execute)      | Open apps, web search, stats  |
| 2     | Confirm required         | Delete files, install software|
| 3     | Restricted/Forbidden     | System32, registry, shutdown  |

## Dependencies
- google-generativeai (Gemini API)
- pyautogui, playwright (automation)
- opencv-python, pytesseract, mss (vision)
- openai-whisper, pyttsx3 (voice)
- faiss-cpu, sentence-transformers (memory)
- fastapi, uvicorn, websockets (dashboard)
- beautifulsoup4, trafilatura, duckduckgo_search (research)
- psutil, numpy, requests, aiohttp (core utilities)
