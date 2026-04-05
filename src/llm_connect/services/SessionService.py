from fastapi import BackgroundTasks

from llm_connect import logger
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.immerse.Orchestrator import Orchestrator


class SessionService:
    def __init__(
        self,
        orchestrator: Orchestrator,
        session_repo: SessionRepository,
        activity_repo: ActivityRepository,
        con_repo: ConversationRepository,
    ):
        self.o = orchestrator
        self.session_repo = session_repo
        self.activity_repo = activity_repo
        self.con_repo = con_repo

    def get_session(self, session_id: str):
        return self.session_repo.get_session_by_id(session_id)

    async def handle_interaction(
        self,
        session_id: str,
        content: str,
        engine: BackgroundTasks,
    ):
        logger.info("🈶 Session service started")

        # Manually yield the result
        async for token in self.o.start(
            session_id,
            content,
            engine,
        ):
            yield token

    async def get_current_goal(self, session_id):
        session = self.session_repo.get_session_by_id(session_id)
        activity_id = session["activity_id"]
        goal_id = session["current_goal"]
        goal = self.activity_repo.get_goal_by_id(
            activity_id=activity_id,
            goal_id=goal_id,
        )
        return goal, session["status"]

    def new_session(self, learner_id: str, activity_id: str):
        con_id = self.con_repo.create_new_conversation(type="EMBEDDED")

        session = self.session_repo.create_session(
            activity_id,
            con_id,
        )

        return session
