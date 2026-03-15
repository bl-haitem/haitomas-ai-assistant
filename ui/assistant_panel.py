"""
HAITOMAS ASSISTANT — Desktop Assistant Panel
Floating desktop HUD with PyQt6 (falls back to Tkinter).
"""
import sys
import threading

# Try PyQt6 first, then Tkinter
try:
    from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                                  QLabel, QLineEdit, QFrame, QGraphicsDropShadowEffect,
                                  QPushButton)
    from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject, QPoint
    from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QFont

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Dummy classes for fallback stability
    class QObject: pass
    class QWidget: pass
    def pyqtSignal(*args, **kwargs):
        class MockSignal:
            def connect(self, func): pass
            def emit(self, *args): pass
        return MockSignal()


class SignalBridge(QObject):
    """Thread-safe signal bridge for updating UI from background threads."""
    update_signal = pyqtSignal(str, str)  # text, panel


class ArcReactor(QWidget):
    """Animated pulsing core indicator."""
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE: return
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self._pulse = 0
        self._direction = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def _animate(self):
        try:
            # Dynamic speed based on status
            speed = 1.5
            if hasattr(self.parent(), 'status'):
                status_text = self.parent().status.text().upper()
                if "ANALYZING" in status_text or "PROCESSING" in status_text or "CAPTURING" in status_text:
                    speed = 4.0 # High energy pulse
            
            self._pulse += speed * self._direction
            if self._pulse > 35 or self._pulse < 0:
                self._direction *= -1
            self.update()
        except:
            pass

    def paintEvent(self, event):
        if not PYQT_AVAILABLE: return
        try:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            cx, cy = self.width() // 2, self.height() // 2

            # Outer rings
            p.setPen(QPen(QColor(0, 195, 255, 80), 1.5))
            for i in range(3):
                r = int(30 + i * 12 + self._pulse / 4)
                p.drawEllipse(QRect(cx - r, cy - r, r * 2, r * 2))

            # Inner glow
            size = int(20 + self._pulse / 8)
            grad = QRadialGradient(float(cx), float(cy), float(30))
            grad.setColorAt(0, QColor(200, 255, 255, 255))
            grad.setColorAt(1, QColor(0, 150, 255, 120))
            p.setBrush(grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRect(cx - size, cy - size, size * 2, size * 2))
            p.end()
        except:
            pass


class AssistantPanel(QWidget):
    """Futuristic Glassmorphic HUD for Haitomas."""

    def __init__(self, command_callback, voice_callback=None):
        if not PYQT_AVAILABLE: return
        super().__init__()
        self.command_callback = command_callback
        self.voice_callback = voice_callback

        # Signal bridge for thread-safe UI updates
        self.bridge = SignalBridge()
        self.bridge.update_signal.connect(self._do_update)

        self._dragging = False
        self._build_ui()
        
        # Upper center placement
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - 550) / 2), 70)
        self.show()

    def _build_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main HUD Body (Glassmorphism)
        self.frame = QFrame(self)
        self.frame.setObjectName("MainHUD")
        self.frame.setStyleSheet("""
            QFrame#MainHUD {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 rgba(10, 28, 50, 240), 
                            stop:1 rgba(5, 15, 30, 220));
                border: 2px solid rgba(0, 195, 255, 180);
                border-radius: 24px;
            }
        """)

        # Neon Outer Glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 195, 255, 120))
        shadow.setOffset(0, 0)
        self.frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        self.content_layout = QVBoxLayout(self.frame)
        self.content_layout.setContentsMargins(25, 25, 25, 25)
        self.content_layout.setSpacing(20)

        # --- HEADER (Reactor + Status) ---
        header = QHBoxLayout()
        self.reactor = ArcReactor(self)
        header.addWidget(self.reactor)
        
        info_box = QVBoxLayout()
        self.title_label = QLabel("HAITOMAS COMMANDER")
        self.title_label.setStyleSheet("""
            color: #ffffff; 
            font-weight: bold; 
            font-family: 'Segoe UI Semibold', 'Outfit'; 
            font-size: 22px; 
            letter-spacing: 1.5px;
        """)
        
        self.status = QLabel("● SYSTEM: STABLE")
        self.status.setStyleSheet("color: #00f0ff; font-family: 'Consolas'; font-size: 15px; font-weight: bold;")
        
        info_box.addWidget(self.title_label)
        info_box.addWidget(self.status)
        header.addLayout(info_box)
        header.addStretch()
        
        self.tag_label = QLabel("v2.5 // PRO")
        self.tag_label.setStyleSheet("color: rgba(0, 195, 255, 120); font-family: 'Consolas'; font-size: 11px; border: 1px solid rgba(0,195,255,40); border-radius: 5px; padding: 2px 7px;")
        header.addWidget(self.tag_label, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.content_layout.addLayout(header)

        # --- CENTRAL CONSOLE (Logs) ---
        from PyQt6.QtWidgets import QScrollArea
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: rgba(0, 12, 24, 160); border: 1px solid rgba(0, 195, 255, 45); border-radius: 15px;")
        
        self.log = QLabel("Quantum links active.\nAwaiting voice or text input...")
        self.log.setWordWrap(True)
        self.log.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log.setStyleSheet("""
            color: rgba(230, 245, 255, 0.95); 
            font-family: 'Consolas', 'JetBrains Mono'; 
            font-size: 15px; 
            padding: 18px;
            line-height: 1.5;
        """)
        
        self.scroll.setWidget(self.log)
        self.scroll.setMinimumHeight(170)
        self.content_layout.addWidget(self.scroll)

        # --- QUICK ACCESS TOOLS ---
        tools_row = QHBoxLayout()
        tool_btn_style = """
            QPushButton {
                background: rgba(0, 195, 255, 18);
                border: 1px solid rgba(0, 195, 255, 70);
                border-radius: 10px;
                color: #00f0ff;
                font-family: 'Consolas';
                font-size: 12px;
                padding: 7px 15px;
            }
            QPushButton:hover {
                background: rgba(0, 195, 255, 50);
                border: 1px solid #00f0ff;
                color: white;
            }
        """
        self.btn_web = QPushButton("🌐 BROWSER")
        self.btn_web.setStyleSheet(tool_btn_style)
        self.btn_web.clicked.connect(lambda: self.command_callback("open google"))
        
        self.btn_reset = QPushButton("🧹 PURGE")
        self.btn_reset.setStyleSheet(tool_btn_style)
        self.btn_reset.clicked.connect(lambda: self.log.setText("Interface state reset."))

        tools_row.addWidget(self.btn_web)
        tools_row.addWidget(self.btn_reset)
        tools_row.addStretch()
        self.content_layout.addLayout(tools_row)

        # --- COMMAND INPUT SECTION ---
        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter system command...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(5, 15, 30, 230);
                border: 1px solid rgba(0, 195, 255, 130);
                border-radius: 16px;
                color: white;
                padding: 16px;
                font-family: 'Segoe UI';
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #00f0ff;
                background: rgba(0, 35, 70, 240);
            }
        """)
        self.input_field.returnPressed.connect(self._submit)
        
        # The Ionic Core (Mic Button)
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(62, 62)
        self.mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_mic_ready()
        
        if self.voice_callback:
            self.mic_btn.clicked.connect(self.voice_callback)

        input_row.addWidget(self.input_field)
        input_row.addWidget(self.mic_btn)
        self.content_layout.addLayout(input_row)

        layout.addWidget(self.frame)
        self.setLayout(layout)
        self.resize(560, 460)

    def _set_mic_ready(self):
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, 
                            stop:0 rgba(0, 160, 255, 255), 
                            stop:1 rgba(0, 40, 80, 255));
                border: 2px solid #00c3ff;
                border-radius: 31px;
                color: white;
                font-size: 24px;
            }
            QPushButton:hover {
                border: 3px solid #00f0ff;
                font-size: 26px;
            }
        """)

    def _submit(self):
        text = self.input_field.text().strip()
        if text:
            self.log.setText(self.log.text() + f"\n\n[USER]: {text}")
            self.input_field.clear()
            self.command_callback(text)

    def update_text(self, text: str, panel: str = "chat"):
        """Thread-safe text update."""
        if PYQT_AVAILABLE:
            self.bridge.update_signal.emit(text, panel)

    def _do_update(self, text: str, panel: str):
        """Actual UI update (runs on main thread)."""
        text_up = text.upper()
        
        if panel == "strategy":
            self.status.setText(f"⚙️ {text.upper()}")
            self.log.setText(self.log.text() + f"\n[ANALYSIS] {text}")
        else:
            self.log.setText(self.log.text() + f"\n{text}")
        
        # Scroll logic
        QTimer.singleShot(70, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

        # --- DYNAMIC VISUAL REACTION ---
        if "ERROR" in text_up or "❌" in text:
            self.status.setText("● SYSTEM: FAULT")
            self.status.setStyleSheet("color: #ff4d4d; font-weight: bold; font-family: 'Consolas';")
            self.mic_btn.setStyleSheet("background: #700; border: 3px solid #f55; border-radius: 31px; color: white; font-size: 24px;")
        
        elif "LISTENING" in text_up:
            self.status.setText("● SYSTEM: CAPTURING...")
            self.status.setStyleSheet("color: #ffcc00; font-weight: bold; font-family: 'Consolas';")
            self.mic_btn.setStyleSheet("background: #ffcc00; border: 4px solid #fff; border-radius: 31px; color: black; font-size: 30px; font-weight: bold;")
            
        elif "TRANSCRIBING" in text_up or "PLANNING" in text_up:
            self.status.setText("● SYSTEM: THINKING...")
            self.status.setStyleSheet("color: #c39bd3; font-weight: bold; font-family: 'Consolas';")
            self.mic_btn.setStyleSheet("background: #6c3483; border: 3px solid #c39bd3; border-radius: 31px; color: white; font-size: 24px;")

        elif "HEARD:" in text_up or "SUCCESS" in text_up or "COMPLETE" in text_up:
            self.status.setText("● SYSTEM: STABLE")
            self.status.setStyleSheet("color: #2ecc71; font-weight: bold; font-family: 'Consolas';")
            self._set_mic_ready()

    # Smooth Window Movement
    def mousePressEvent(self, event):
        if PYQT_AVAILABLE and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = event.position().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if PYQT_AVAILABLE and hasattr(self, '_dragging') and self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def run(self):
        if not PYQT_AVAILABLE: return
        app = QApplication.instance()
        if app:
            sys.exit(app.exec())


def create_panel(command_callback, voice_callback=None):
    """Factory function — creates the best available panel."""
    # Ensure a QApplication exists
    if PYQT_AVAILABLE:
        app = QApplication.instance() or QApplication(sys.argv)
        try:
            return AssistantPanel(command_callback, voice_callback)
        except Exception as e:
            print(f"[Panel] PyQt6 initialization failed: {e}")
    
    # Fallback to Tkinter
    try:
        from ui.overlay import FloatingAssistantUI
        return FloatingAssistantUI(command_callback, voice_callback)
    except Exception as e:
        print(f"[Panel] Fallback UI failed: {e}")
        return None
