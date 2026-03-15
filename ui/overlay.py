import tkinter as tk
from tkinter import font, scrolledtext
import threading
import time
import os

class FloatingAssistantUI:
    """The 'Architect' Dashboard: A modern, multi-panel intelligence interface."""
    def __init__(self, callback, voice_callback=None):
        self.callback = callback
        self.voice_callback = voice_callback
        self.root = tk.Tk()
        self.root.title("HAITOMAS ARCHITECT CORE")
        self.is_expanded = True # Start expanded for Architect mode
        self.setup_ui()

    def setup_ui(self):
        # Window attributes
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95) # Slight transparency
        
        # Sizing and Positioning
        self.w, self.h = 900, 550
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        # Position at the center-right
        self.root.geometry(f"{self.w}x{self.h}+{self.screen_h - 100}+{50}")

        # Modern Palette
        self.bg_dark = "#0a0b10"
        self.bg_panel = "#161b22"
        self.accent_blue = "#58a6ff"
        self.accent_pink = "#ff79c6"
        self.text_main = "#c9d1d9"
        self.text_dim = "#8b949e"

        # Main Layout Container
        self.main_container = tk.Frame(self.root, bg=self.bg_dark, highlightthickness=1, highlightbackground=self.accent_blue)
        self.main_container.pack(fill="both", expand=True)

        # 1. TOP HEADER (Navigation & Move)
        self.header = tk.Frame(self.main_container, bg=self.bg_dark, height=40)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.title_label = tk.Label(self.header, text="HAITOMAS // ARCHITECT LEVEL 4", fg=self.accent_blue, bg=self.bg_dark, font=("Consolas", 9, "bold"))
        self.title_label.pack(side="left", padx=15)

        self.close_btn = tk.Button(self.header, text="✕", fg=self.text_dim, bg=self.bg_dark, bd=0, command=self.root.destroy, font=("Arial", 10), activebackground="#ff4444")
        self.close_btn.pack(side="right", padx=10)
        
        # 2. PANELS (Left: Chat | Right: Strategic Visualization)
        self.panels_frame = tk.Frame(self.main_container, bg=self.bg_dark)
        self.panels_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # --- LEFT PANEL: Chat Console ---
        self.left_panel = tk.Frame(self.panels_frame, bg=self.bg_panel, width=480, highlightthickness=1, highlightbackground="#30363d")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=5)
        self.left_panel.pack_propagate(False)

        self.chat_label = tk.Label(self.left_panel, text="COMMUNICATION INTERFACE", fg=self.text_dim, bg=self.bg_panel, font=("Consolas", 8))
        self.chat_label.pack(anchor="w", padx=10, pady=5)

        self.chat_area = scrolledtext.ScrolledText(
            self.left_panel, bg=self.bg_panel, fg=self.text_main, font=("Segoe UI", 10),
            borderwidth=0, highlightthickness=0, padx=10, pady=10, state='disabled'
        )
        self.chat_area.pack(fill="both", expand=True)

        # --- RIGHT PANEL: Strategy & Research ---
        self.right_panel = tk.Frame(self.panels_frame, bg=self.bg_panel, width=380, highlightthickness=1, highlightbackground="#30363d")
        self.right_panel.pack(side="right", fill="both", padx=5)
        self.right_panel.pack_propagate(False)

        self.strat_label = tk.Label(self.right_panel, text="STRATEGIC REASONING & RESEARCH", fg=self.accent_pink, bg=self.bg_panel, font=("Consolas", 8))
        self.strat_label.pack(anchor="w", padx=10, pady=5)

        self.strat_area = scrolledtext.ScrolledText(
            self.right_panel, bg=self.bg_panel, fg="#8be9fd", font=("Consolas", 9),
            borderwidth=0, highlightthickness=0, padx=10, pady=10, state='disabled'
        )
        self.strat_area.pack(fill="both", expand=True)

        # 3. BOTTOM INPUT AREA
        self.input_frame = tk.Frame(self.main_container, bg=self.bg_dark, height=60)
        self.input_frame.pack(fill="x", side="bottom")
        self.input_frame.pack_propagate(False)

        self.input_entry = tk.Entry(
            self.input_frame, bg=self.bg_panel, fg=self.accent_blue, insertbackground=self.accent_blue,
            borderwidth=0, font=("Segoe UI", 12), highlightthickness=1, highlightbackground="#30363d"
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(15, 5), pady=10)
        self.input_entry.bind("<Return>", self.on_input)
        self.input_entry.focus_set()

        if self.voice_callback:
            self.mic_btn = tk.Button(self.input_frame, text="🎤", bg=self.bg_panel, fg=self.accent_blue, bd=0, font=("Arial", 14), command=self.on_mic)
            self.mic_btn.pack(side="right", padx=15)

        # 4. STATUS BAR
        self.status_bar = tk.Frame(self.main_container, bg=self.bg_dark, height=20)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_text = tk.Label(self.status_bar, text="SYSTEM STATUS: NOMINAL", fg=self.text_dim, bg=self.bg_dark, font=("Consolas", 7))
        self.status_text.pack(side="left", padx=15)

        # Bindings
        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)
        
        self.update_chat("Haitomas Architect Interface loaded. Awaiting directive.")

    def update_chat(self, text):
        self._write_to_area(self.chat_area, text, "haitomas")

    def update_text(self, text, panel="chat"):
        """Routes text to either chat or strategy panel based on indicators."""
        if panel == "strategy" or "■" in text or "REASONING" in text or "INTELLIGENCE REPORT" in text:
            self._write_to_area(self.strat_area, text, "system")
            # Also notify chat for important state changes
            if "■" in text:
                self.update_status(text.replace("■", "").strip())
        else:
            self.update_chat(text)

    def update_status(self, text):
        self.status_text.config(text=f"SYSTEM STATUS: {text.upper()}")
        self.root.update_idletasks()

    def _write_to_area(self, area, text, sender):
        area.config(state='normal')
        prefix = "\n" if area.get("1.0", tk.END).strip() else ""
        area.insert(tk.END, f"{prefix}[{sender.upper()}] {text}\n")
        area.see(tk.END)
        area.config(state='disabled')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def on_mic(self):
        self.status_text.config(text="SYSTEM STATUS: LISTENING...")
        if self.voice_callback:
            threading.Thread(target=self.voice_callback, daemon=True).start()

    def on_input(self, event):
        cmd = self.input_entry.get()
        if not cmd: return
        self.input_entry.delete(0, tk.END)
        self._write_to_area(self.chat_area, cmd, "user")
        self.update_status("THINKING...")
        threading.Thread(target=self.callback, args=(cmd,), daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ui = FloatingAssistantUI(lambda x: print(x))
    ui.run()
