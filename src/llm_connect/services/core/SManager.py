from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.SessionRepository import SessionRepository


# FIXME: Not important right now
class SManager:
    def __init__(
        self,
        session_repo: SessionRepository,
        activity_repo: ActivityRepository,
        conversation_repo: ConversationRepository,
    ):
        self.session_repo = session_repo
        self.activity_repo = activity_repo
        self.conversation_repo = conversation_repo

    def load_metadata():
        None
