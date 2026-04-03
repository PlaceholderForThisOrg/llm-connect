from fastapi import BackgroundTasks

from llm_connect import logger
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.immerse.Orchestrator import Orchestrator


class SessionService:
    def __init__(
        self,
        orchestrator: Orchestrator,
        session_repo: SessionRepository,
        activity_repo: ActivityRepository,
    ):
        self.o = orchestrator
        self.session_repo = session_repo
        self.activity_repo = activity_repo

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
        session = self.session_repo.get_session_by_id("")
        goal_id = session["current_goal"]
        goal = self.activity_repo.get_goal_by_id(activity_id="", goal_id=goal_id)
        return goal, session["status"]
