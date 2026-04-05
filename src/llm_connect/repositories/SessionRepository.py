import json
from pathlib import Path

from llm_connect.proto.session.session_v2 import session_v2


class SessionRepository:
    def __init__(self):
        self.file_path = (
            Path(__file__).resolve().parent.parent
            / "proto"
            / "runtime_db"
            / "session_v2.json"
        )

        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing session if exists
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session_v2.update(data)
            except Exception:
                # Ignore for prototype (corrupt or empty file)
                pass

        # Initial sync (ensures file exists)
        self.sync()

    def sync(self):
        """Persist session to disk"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(session_v2, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[session sync error] {e}")

    def get_session_by_id(self, session_id: str):
        # Prototype: single session
        return session_v2

    def get_current_checkpoint(self, session_id: str):
        return session_v2.get("current_goal")

    def update_next_checkpoint(self, session_id, checkpoint_id: str):
        session_v2["current_goal"] = checkpoint_id
        self.sync()

    def add_interaction(self, session_id, interaction):
        if "history" not in session_v2:
            session_v2["history"] = []

        session_v2["history"].append(interaction)
        self.sync()
