from llm_connect.proto.session import session


class SessionRepository:
    def __init__(self):
        pass

    def get_session_by_id(self, session_id: str):
        return session

    def get_current_checkpoint(self, session_id: str):
        return session["checkpoint"]
