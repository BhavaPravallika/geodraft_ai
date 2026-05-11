"""
services/session_store.py
Wrapper for state persistence if we want to save states to disk or database later.
Currently it bridges with core/state_manager.py.
"""
from core.state_manager import StateManager

class SessionStore:
    @staticmethod
    def save_recent_export(filename, metadata):
        """Mock persistence: in a real app, save to a DB or local file."""
        if "recent_exports" not in StateManager.get("cad_settings", {}):
            StateManager.get("cad_settings", {})["recent_exports"] = []
            
        StateManager.get("cad_settings")["recent_exports"].append({
            "filename": filename,
            "metadata": metadata
        })
