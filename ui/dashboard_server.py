"""
HAITOMAS ASSISTANT — Dashboard Server
FastAPI + WebSocket real-time dashboard for monitoring the assistant.
"""
import json
import asyncio
import threading
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, FileResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_COMMAND_EXECUTED, EVENT_ERROR
from config.settings import DASHBOARD_HOST, DASHBOARD_PORT


class DashboardServer:
    """Real-time web dashboard for HAITOMAS monitoring."""

    def __init__(self, assistant_loop=None):
        if not FASTAPI_AVAILABLE:
            print("[Dashboard] FastAPI not installed. Dashboard disabled.")
            return

        self.assistant = assistant_loop
        self.app = FastAPI(title="HAITOMAS Dashboard")
        self.connections: list[WebSocket] = []
        self.activity_log: list[dict] = []

        self._setup_routes()
        self._subscribe_events()

    def _setup_routes(self):
        """Configure API routes."""
        static_dir = Path(__file__).parent / "static"
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        # Serve the dashboard HTML
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            index_file = static_dir / "index.html"
            if index_file.exists():
                return index_file.read_text(encoding="utf-8")
            return "<h1>HAITOMAS Dashboard</h1><p>Static files not found.</p>"

        # Serve static files
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        # WebSocket for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(ws: WebSocket):
            await ws.accept()
            self.connections.append(ws)
            try:
                # Send initial state
                await ws.send_json({
                    "type": "init",
                    "activity": self.activity_log[-50:],
                    "stats": self._get_stats()
                })

                while True:
                    data = await ws.receive_text()
                    msg = json.loads(data)

                    if msg.get("type") == "command" and self.assistant:
                        user_input = msg.get("text", "")
                        if user_input:
                            self.assistant.process(user_input)

            except WebSocketDisconnect:
                if ws in self.connections:
                    self.connections.remove(ws)
            except Exception:
                if ws in self.connections:
                    self.connections.remove(ws)

        # REST API endpoints
        @self.app.get("/api/stats")
        async def get_stats():
            return self._get_stats()

        @self.app.get("/api/activity")
        async def get_activity():
            return {"activity": self.activity_log[-100:]}

        @self.app.post("/api/command")
        async def send_command(data: dict):
            if self.assistant:
                self.assistant.process(data.get("text", ""))
                return {"status": "processing"}
            return {"status": "error", "message": "Assistant not connected"}

    def _subscribe_events(self):
        """Subscribe to event bus for real-time updates."""
        event_bus.subscribe(EVENT_UI_UPDATE, self._on_update)
        event_bus.subscribe(EVENT_COMMAND_EXECUTED, self._on_command)
        event_bus.subscribe(EVENT_ERROR, self._on_error)

    def _on_update(self, data: dict):
        entry = {
            "type": "update",
            "text": data.get("text", ""),
            "panel": data.get("panel", "chat"),
            "time": datetime.now().isoformat()
        }
        self.activity_log.append(entry)
        self._broadcast(entry)

    def _on_command(self, data: dict):
        entry = {
            "type": "command_executed",
            "command": data.get("command", ""),
            "result": data.get("result", ""),
            "time": datetime.now().isoformat()
        }
        self.activity_log.append(entry)
        self._broadcast(entry)

    def _on_error(self, data: dict):
        entry = {
            "type": "error",
            "message": data.get("message", ""),
            "time": datetime.now().isoformat()
        }
        self.activity_log.append(entry)
        self._broadcast(entry)

    def _broadcast(self, data: dict):
        """Send data to all connected WebSocket clients (thread-safe)."""
        if not self.connections:
            return

        async def _sender():
            for ws in self.connections[:]:
                try:
                    await ws.send_json(data)
                except Exception:
                    if ws in self.connections:
                        self.connections.remove(ws)

        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(_sender(), self.loop)
        else:
            # Fallback if loop is not yet running or accessible
            try:
                new_loop = asyncio.new_event_loop()
                new_loop.run_until_complete(_sender())
                new_loop.close()
            except Exception:
                pass

    def _get_stats(self) -> dict:
        """Get current system stats."""
        try:
            import psutil
            return {
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "total_commands": len(self.activity_log),
                "uptime": datetime.now().isoformat()
            }
        except Exception:
            return {"cpu": 0, "ram": 0, "total_commands": len(self.activity_log)}

    def start(self):
        """Start the dashboard server in a background thread."""
        if not FASTAPI_AVAILABLE:
            return

        def _run():
            uvicorn.run(
                self.app,
                host=DASHBOARD_HOST,
                port=DASHBOARD_PORT,
                log_level="warning"
            )

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        print(f"[Dashboard] Running at http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
