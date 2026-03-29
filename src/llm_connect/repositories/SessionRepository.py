from llm_connect.proto.session import session


class SessionRepository:
    def __init__(self):
        pass

    def get_session_by_id(self, session_id: str):
        return session

    def get_current_checkpoint(self, session_id: str):
        return session["checkpoint"]

    def update_next_checkpoint(self, session_id, checkpoint_id: str):
        session["checkpoint"] = checkpoint_id
