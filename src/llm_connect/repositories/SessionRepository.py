from llm_connect.proto.session.session_v2 import session_v2


class SessionRepository:
    def __init__(self):
        pass

    def get_session_by_id(self, session_id: str):
        return session_v2

    def get_current_checkpoint(self, session_id: str):
        return session_v2["current_goal"]

    def update_next_checkpoint(self, session_id, checkpoint_id: str):
        session_v2["current_goal"] = checkpoint_id
