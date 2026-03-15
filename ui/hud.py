import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QPointF, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QLinearGradient, QFont, QPolygonF

class ArcReactor(QWidget):
    """Futuristic animated core with multi-layer pulsing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self._pulse = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pulse)
        self.timer.start(50)
        self.pulse_direction = 1

    def update_pulse(self):
        self._pulse += 1.5 * self.pulse_direction
        if self._pulse > 35 or self._pulse < 0:
            self.pulse_direction *= -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        cx = int(rect.center().x())
        cy = int(rect.center().y())
        
        # Outer Hexagon Glow
        painter.setPen(QPen(QColor(0, 195, 255, 100), 2))
        for i in range(3):
            size = int(50 + i*15 + self._pulse/4)
            painter.drawEllipse(QRect(cx - size, cy - size, size * 2, size * 2))
            
        # Inner Core
        core_size = int(30 + self._pulse/10)
        gradient = QRadialGradient(float(cx), float(cy), float(40))
        gradient.setColorAt(0, QColor(200, 255, 255, 255))
        gradient.setColorAt(1, QColor(0, 150, 255, 150))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRect(cx - core_size, cy - core_size, core_size * 2, core_size * 2))

class TelemetryBar(QWidget):
    """Small animated progress bar for aesthetic feedback."""
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 20)
        self.label_text = label
        self.value = 50
        self.target = 50
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(100)

    def animate(self):
        import random
        self.target = random.randint(30, 90)
        if abs(self.value - self.target) > 1:
            self.value += (self.target - self.value) * 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Label
        painter.setPen(QColor(0, 195, 255, 200))
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(0, 12, self.label_text)
        
        # Track
        painter.setBrush(QColor(0, 195, 255, 30))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(80, 5, 110, 8)
        
        # Bar
        painter.setBrush(QColor(0, 195, 255, 180))
        w = int(110 * (self.value / 100))
        painter.drawRect(80, 5, w, 8)

class FuturisticHUD(QWidget):
    """Interactive Premium HUD with Text Input and Visual Feedback."""
    def __init__(self, command_callback, voice_callback=None):
        super().__init__()
        self.command_callback = command_callback
        self.voice_callback = voice_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main Container with Blur/Glass Effect
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("MainHUD")
        self.main_frame.setStyleSheet("""
            QFrame#MainHUD {
                background: rgba(10, 20, 30, 210);
                border: 1px solid rgba(0, 195, 255, 100);
                border-radius: 15px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 195, 255, 150))
        shadow.setOffset(0, 0)
        self.main_frame.setGraphicsEffect(shadow)
        
        self.layout = QVBoxLayout(self.main_frame)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Header: Arc Reactor
        self.reactor = ArcReactor()
        reactor_layout = QHBoxLayout()
        reactor_layout.addStretch()
        reactor_layout.addWidget(self.reactor)
        reactor_layout.addStretch()
        self.layout.addLayout(reactor_layout)
        
        # Status & Telemetry
        self.status_label = QLabel("SYSTEM: ACTIVE")
        self.status_label.setStyleSheet("color: #00f0ff; font-family: 'Consolas'; font-size: 14px; font-weight: bold;")
        self.layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(TelemetryBar("CORE_SYNC"))
        self.layout.addWidget(TelemetryBar("NEURAL_LINK"))
        
        # Output Log
        self.log_label = QLabel("haitomas Online. Awaiting Directives...")
        self.log_label.setWordWrap(True)
        self.log_label.setFixedWidth(280)
        self.log_label.setMinimumHeight(60)
        self.log_label.setStyleSheet("color: rgba(200, 240, 255, 220); font-family: 'Segoe UI'; font-size: 12px;")
        self.layout.addWidget(self.log_label)
        
        # TEXT INPUT FIELD (Premium Design)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type command...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 50, 80, 150);
                border: 1px solid #00c3ff;
                border-radius: 5px;
                color: white;
                padding: 8px;
                font-family: 'Consolas';
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00f0ff;
                background: rgba(0, 80, 120, 180);
            }
        """)
        self.input_field.returnPressed.connect(self.submit_command)
        self.layout.addWidget(self.input_field)
        
        # Footer Hint
        hint = QLabel("Press Enter to execute | Click to Drag")
        hint.setStyleSheet("color: rgba(0, 195, 255, 100); font-size: 9px; font-family: 'Consolas';")
        self.layout.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set Layout and Show
        container_layout = QVBoxLayout(self)
        container_layout.addWidget(self.main_frame)
        self.setLayout(container_layout)
        self.show()
        
        # Set Position
        screen = QApplication.primaryScreen().geometry()
        self.setFixedSize(340, 480)
        self.move(screen.width() - 360, 50)

    def submit_command(self):
        text = self.input_field.text().strip()
        if text:
            self.update_text(f"Executing: {text}")
            self.input_field.clear()
            # Send to assistant
            self.command_callback(text)

    def update_text(self, text):
        self.log_label.setText(text[:300] + "..." if len(text) > 300 else text)
        if "ERROR" in text.upper() or "ANOMALY" in text.upper():
            self.status_label.setText("SYSTEM: ANOMALY")
            self.status_label.setStyleSheet("color: #ff3c3c; font-family: 'Consolas'; font-size: 14px;")
        else:
            self.status_label.setText("SYSTEM: PROCESSING")
            self.status_label.setStyleSheet("color: #00f0ff; font-family: 'Consolas'; font-size: 14px;")

    def run(self):
        app = QApplication.instance()
        if app:
            sys.exit(app.exec())

    # Drag and Drop support
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = FuturisticHUD(lambda x: print(f"Executing: {x}"))
    sys.exit(app.exec())
