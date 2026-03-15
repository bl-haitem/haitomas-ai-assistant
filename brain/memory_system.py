import sqlite3
import json
import time

class LightweightMemory:
    """SQL-based context memory for minimal RAM footprint."""
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.setup()

    def setup(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT,
                    bot_response TEXT,
                    metadata TEXT
                )
            """)

    def add_interaction(self, user_input, response, metadata=None):
        meta_json = json.dumps(metadata) if metadata else "{}"
        with self.conn:
            self.conn.execute(
                "INSERT INTO history (user_input, bot_response, metadata) VALUES (?, ?, ?)",
                (user_input, response, meta_json)
            )

    def get_context(self, limit=5):
        """Fetch the last N interactions as a list of strings."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_input, bot_response FROM history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [f"User: {r[0]} | Jarvis: {r[1]}" for r in reversed(rows)]

# Watchdog Logic (Conceptual)
"""
How to implement a Watchdog in Windows:

1. Create a script `watchdog.py`.
2. Use `subprocess.Popen` to start `main.py`.
3. Periodically check `process.poll()`.
4. If process died, restart it.

Example Code Snippet for watchdog.py:

import subprocess
import time

def monitor():
    while True:
        process = subprocess.Popen(['python', 'main.py'])
        print(f"Assistant started with PID {process.pid}")
        process.wait()  # Wait for it to exit/crash
        print("Assistant crashed. Restarting in 2 seconds...")
        time.sleep(2)

"""

if __name__ == "__main__":
    mem = LightweightMemory(":memory:") # Use RAM for demo
    mem.add_interaction("Open Chrome", "Opening Google Chrome...")
    print("Recent Memory:", mem.get_context())
