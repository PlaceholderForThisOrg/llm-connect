import json
import os
import uuid

from llm_connect.proto.conversations_v1 import conversations_v1


class ConversationRepository:
    def __init__(self):
        self.file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../proto/runtime_db/conversations.json"
            )
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Load existing data if file exists
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conversations_v1.update(data)
            except Exception:
                # If file is corrupted or empty, ignore for prototype
                pass

        # Initial sync to ensure file exists
        self.sync()

    def sync(self):
        """Write current conversations to file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(conversations_v1, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[sync error] {e}")

    def create_new_conversation(self, type: str):
        """Create a new conversation and persist it"""
        con_id = str(uuid.uuid4())

        conversations_v1[con_id] = {
            "id": con_id,
            "type": type,
            "messages": [],
        }

        self.sync()
        return con_id

    def get_conversation_by_id(self, con_id):
        return conversations_v1.get(con_id)

    def add_new_message(self, con_id, message):
        conversations_v1[con_id]["messages"].append(message)
        self.sync()
