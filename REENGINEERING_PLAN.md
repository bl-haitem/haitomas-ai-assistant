# Jarvis-style High-Performance Optimizer Plan

## 1. System Architecture: Event-Driven Non-Blocking
The assistant will shift from a sequential flow to a **Central Event Bus** architecture. This ensures that a heavy LLM call doesn't freeze the voice listener or the UI.

- **Messaging**: Use `asyncio.Queue` for internal communication.
- **Isolation**: Heavy engines (STT, LLM, TTS) run in separate `multiprocessing` workers to leverage multiple CPU cores.

## 2. Command Routing (The "Bypass" Strategy)
Most commands (70%) are predictable. We use a tri-tier routing system:
1. **Direct Match (O(1))**: Regex/Keywords (e.g., "Open Chrome"). Latency: <5ms.
2. **Intent Classifier (O(log n))**: Small Transformer model (e.g., BERT-tiny) to map text to functions. Latency: <30ms.
3. **LLM Reasoning**: Only for multi-step tasks or complex queries. Latency: 500ms - 2s.

## 3. Concurrency Model
- **AsyncIO**: Main loop handles I/O and UI.
- **Threadpool**: I/O-bound tasks (TTS playing, file browsing).
- **ProcessPool**: CPU-bound tasks (Ollama, Whisper inference).

## 4. Ultra-Low Latency Voice
- **Wake Word**: `OpenWakeWord` (local, lightweight, extremely fast).
- **STT**: `Faster-Whisper` with VAD (Voice Activity Detection). We start processing chunks *while* the user is still speaking.
- **TTS**: `Piper` (pre-compiled C++) or `Kokoro-82M`. These generate audio in milliseconds.

## 5. Memory & Context
- **Short-term**: Sliding window in RAM.
- **Long-term**: `SQLite` with FTS5 (Full Text Search) instead of heavy Vector DBs for simple system tasks, keeping RAM usage < 100MB.

## 6. Crash Protection
- A **Watchdog process** monitors the main PID. If it hangs or crashes, it restarts the modules automatically.
- Each module has a "Heartbeat".

---

# Scalable Folder Structure

```text
/root
│── main.py                # Main entry (async)
│── config.json            # Global settings
│── .env                   # Environment variables
├── core/
│   ├── bus.py             # Event Bus System
│   ├── manager.py         # Module Lifecycle
├── brain/
│   ├── router.py          # The Bypass Logic
│   ├── llm_client.py      # Async Ollama/Llama.cpp
│   ├── memory.py          # SQLite Memory
├── voice/
│   ├── listener.py        # STT Streaming
│   ├── speaker.py         # TTS Rendering
│   ├── wake_word.py       # "Hey Jarvis" logic
├── automation/
│   ├── sys_ops.py         # Windows API / Keyboard / Mouse
│   ├── security.py        # Command validation
├── ui/
│   ├── backend.py         # UI state management
└── utils/
    ├── metrics.py         # Performance tracking
```
