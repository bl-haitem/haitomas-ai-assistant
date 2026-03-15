"""
HAITOMAS ASSISTANT — File Manager
File and folder operations: copy, move, delete, create, list.
"""
import os
import shutil
from pathlib import Path


class FileManager:
    """Safe file and directory operations."""

    def manage(self, operation: str, source: str = "", destination: str = "") -> str:
        """Execute a file operation."""
        op = operation.lower().strip()

        if op == "copy":
            return self.copy(source, destination)
        elif op == "move":
            return self.move(source, destination)
        elif op == "delete":
            return self.delete(source)
        elif op == "create":
            return self.create(source)
        elif op == "list":
            return self.list_dir(source)
        elif op == "read":
            return self.read_file(source)
        else:
            return f"Unknown file operation: {operation}"

    def copy(self, source: str, destination: str) -> str:
        """Copy a file or directory."""
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(source, destination)
            return f"Copied: {source} → {destination}"
        except Exception as e:
            return f"Copy error: {e}"

    def move(self, source: str, destination: str) -> str:
        """Move a file or directory."""
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            return f"Moved: {source} → {destination}"
        except Exception as e:
            return f"Move error: {e}"

    def delete(self, path: str) -> str:
        """Delete a file or directory (with safety checks)."""
        # Safety: prevent catastrophic deletions
        dangerous = ["windows", "system32", "program files", "users"]
        if any(d in path.lower() for d in dangerous):
            return f"BLOCKED: Cannot delete protected path: {path}"

        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
            else:
                return f"Path not found: {path}"
            return f"Deleted: {path}"
        except Exception as e:
            return f"Delete error: {e}"

    def create(self, path: str) -> str:
        """Create a file or directory."""
        try:
            if "." in os.path.basename(path):
                # It's a file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                Path(path).touch()
                return f"Created file: {path}"
            else:
                os.makedirs(path, exist_ok=True)
                return f"Created directory: {path}"
        except Exception as e:
            return f"Create error: {e}"

    def list_dir(self, path: str) -> str:
        """List contents of a directory."""
        try:
            if not os.path.isdir(path):
                return f"Not a directory: {path}"
            items = os.listdir(path)
            if not items:
                return f"Directory is empty: {path}"
            listing = "\n".join(f"  {'📁' if os.path.isdir(os.path.join(path, i)) else '📄'} {i}" for i in items[:50])
            return f"Contents of {path}:\n{listing}"
        except Exception as e:
            return f"List error: {e}"

    def read_file(self, path: str) -> str:
        """Read text file contents."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return content[:5000]  # Limit output
        except Exception as e:
            return f"Read error: {e}"
