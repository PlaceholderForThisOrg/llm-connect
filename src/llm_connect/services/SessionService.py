import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import BackgroundTasks

from llm_connect import logger
from llm_connect.models import Activity, Progress, Session
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

    async def create_session_from_activity(
        self,
        activity_id: str,
        learner_id: str,
    ) -> Session:

        # get activity from mongodb
        activity = await self.activity_repo.get_by_id(activity_id)

        if not activity:
            raise ValueError("Activity not found")

        # Get the start task
        start_task_id = activity.start_tasks[0]

        # Build the full session record
        session_id = uuid.uuid4()
        session = Session(
            id=session_id,
            activity_id=str(activity.id),
            learner_id=learner_id,
            status="IN_PROGRESS",
            progress=0.0,
            started_at=datetime.utcnow(),
            current_task=start_task_id,
            meta={
                "activity_title": activity.metadata.title,
                "total_tasks": len(activity.tasks),
            },
        )

        # build all progresses
        session.progresses = self._build_progress(
            activity,
            session_id,
            start_task_id,
        )

        # persist the session
        return await self.session_repo.create(session)

    def _build_progress(
        self,
        activity: Activity,
        session_id,
        start_task_id: str,
    ) -> List[Progress]:

        progresses: List[Progress] = []
        now = datetime.now(timezone.utc)

        for task_id in activity.tasks.keys():

            is_start = task_id == start_task_id

            progresses.append(
                Progress(
                    session_id=session_id,
                    task_id=task_id,
                    status="UNLOCKED" if is_start else "LOCKED",
                    num_attempts=0,
                    score=None,
                    started_at=now if is_start else None,
                    completed_at=None,
                    meta={"is_start_task": is_start},
                )
            )

        return progresses

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
            "learner_001",
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
