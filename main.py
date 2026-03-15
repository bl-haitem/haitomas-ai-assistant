"""
╔════════════════════════════════════════════════════════╗
║          HAITOMAS ASSISTANT — Main Entry Point          ║
║     Intelligent AI Operating System Controller          ║
║              Powered by Google Gemini AI                ║
╚════════════════════════════════════════════════════════╝

Usage:
    python main.py              → Desktop HUD + Dashboard
    python main.py --console    → Console mode only
    python main.py --dashboard  → Dashboard only (no desktop HUD)
"""
import sys
import os
import warnings
import argparse

# ── Rendering Fix for Windows (UpdateLayeredWindowIndirect failed) ──
if os.name == 'nt':
    os.environ["QT_WIDGETS_RHI"] = "0" # Disable RHI to force software-compatible rendering
    os.environ["QT_OPENGL"] = "software"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

# ── Environment Setup ──
warnings.filterwarnings("ignore")

# Force UTF-8 for Windows Console to prevent charmap errors
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.environ["PATH"] += os.pathsep + r"C:\Users\pc\Desktop"

# Suppress Qt DPI warning on Windows (Qt handles DPI scaling natively)
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_LOGGING_RULES"] = "qt.qpa.window=false"

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_console_mode(assistant):
    """Run the assistant in console mode."""
    print("\n╔══════════════════════════════════════╗")
    print("║   HAITOMAS — Console Mode Active      ║")
    print("╠══════════════════════════════════════╣")
    print("║  Type a command and press Enter        ║")
    print("║  Type 'voice' for voice input          ║")
    print("║  Type 'stats' for system stats         ║")
    print("║  Type 'history' for task history       ║")
    print("║  Type 'exit' to quit                   ║")
    print("╚══════════════════════════════════════╝\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("\n[HAITOMAS] Shutting down. Goodbye, Commander.")
                break
            elif user_input.lower() == "voice":
                try:
                    from voice.speech_to_text import SpeechToText
                    stt = SpeechToText()
                    text = stt.record_and_transcribe()
                    if text:
                        print(f"[Voice] Heard: {text}")
                        assistant.process(text)
                    else:
                        print("[Voice] No speech detected.")
                except Exception as e:
                    print(f"[Voice] Error: {e}")
                continue
            elif user_input.lower() == "stats":
                stats = assistant.memory.get_stats()
                print(f"\n📊 Stats: {stats}\n")
                continue
            elif user_input.lower() == "history":
                history = assistant.memory.get_recent_history(5)
                for h in history:
                    print(f"  [{h.get('type', '?')}] {h.get('command', 'N/A')}")
                continue
            elif user_input.lower() == "clear":
                assistant.gemini.clear_history()
                print("[HAITOMAS] Conversation history cleared.")
                continue

            # Process command
            assistant.process(user_input)

            # Wait a moment for async processing
            import time
            time.sleep(2)

        except KeyboardInterrupt:
            print("\n[HAITOMAS] Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"[Error] {e}")


def run_gui_mode(assistant, args):
    """Run the assistant with Desktop HUD."""
    from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK

    # Start Dashboard server
    if not args.no_dashboard:
        try:
            from ui.dashboard_server import DashboardServer
            dashboard = DashboardServer(assistant)
            dashboard.start()
        except Exception as e:
            print(f"[Dashboard] Could not start: {e}")

    # Create Desktop Panel
    try:
        # Need QApplication before creating widgets
        try:
            from PyQt6.QtWidgets import QApplication
            qt_app = QApplication.instance() or QApplication(sys.argv)
            PYQT = True
        except ImportError:
            PYQT = False
            qt_app = None

        from ui.assistant_panel import create_panel

        def voice_handler():
            def run_recording():
                try:
                    from voice.speech_to_text import SpeechToText
                    stt = SpeechToText()
                    text = stt.record_and_transcribe()
                    if text:
                        assistant.process(text)
                    else:
                        panel.update_text("Could not hear you clearly. Try again, Commander.", "chat")
                except Exception as e:
                    print(f"[Voice] Error: {e}")
            
            import threading
            threading.Thread(target=run_recording, daemon=True).start()

        panel = create_panel(
            command_callback=assistant.process,
            voice_callback=voice_handler
        )

        # Wire event bus to panel
        def on_ui_update(data):
            panel.update_text(data.get("text", ""), data.get("panel", "chat"))

        event_bus.subscribe(EVENT_UI_UPDATE, on_ui_update)

        print("\n[HAITOMAS] Desktop HUD activated.")
        print("[HAITOMAS] Dashboard at http://127.0.0.1:8500")
        print("[HAITOMAS] Ready for your commands, Commander.\n")

        # Run Qt event loop
        if PYQT and qt_app:
            sys.exit(qt_app.exec())
        else:
            panel.run()

    except Exception as e:
        print(f"[UI] GUI failed: {e}")
        print("[UI] Falling back to console mode...")
        run_console_mode(assistant)


def run_dashboard_only(assistant):
    """Run dashboard without desktop HUD."""
    try:
        from ui.dashboard_server import DashboardServer
        import uvicorn

        dashboard = DashboardServer(assistant)
        print(f"\n[HAITOMAS] Dashboard-only mode.")
        print(f"[HAITOMAS] Open http://127.0.0.1:8500 in your browser.\n")

        uvicorn.run(
            dashboard.app,
            host="127.0.0.1",
            port=8500,
            log_level="info"
        )
    except Exception as e:
        print(f"[Dashboard] Error: {e}")
        run_console_mode(assistant)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="HAITOMAS AI Assistant")
    parser.add_argument("--console", action="store_true", help="Run in console mode only")
    parser.add_argument("--dashboard", action="store_true", help="Run dashboard only (no desktop HUD)")
    parser.add_argument("--no-dashboard", action="store_true", help="Disable web dashboard")
    args = parser.parse_args()

    # Initialize the core assistant
    from core.assistant_loop import AssistantLoop
    assistant = AssistantLoop()

    # Choose run mode
    if args.console:
        run_console_mode(assistant)
    elif args.dashboard:
        run_dashboard_only(assistant)
    else:
        run_gui_mode(assistant, args)


if __name__ == "__main__":
    main()