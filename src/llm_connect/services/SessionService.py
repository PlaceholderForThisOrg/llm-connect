import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect import logger
from llm_connect.models import Activity, Progress, Session, TaskType
from llm_connect.models.Conversation import Conversation
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.schemas.session_schema import SessionSearchQuery
from llm_connect.services.immerse.Orchestrator import Orchestrator


class SessionService:
    def __init__(
        self,
        orchestrator: Orchestrator,
        session_repo: SessionRepository,
        activity_repo: ActivityRepository,
        con_repo: ConversationRepository,
        session: AsyncSession,
    ):
        self.orchestrator = orchestrator
        self.repo = session_repo
        self.session_repo = session_repo
        self.activity_repo = activity_repo
        self.conversation_repo = con_repo
        self.session = session

    async def get_session_detail(self, session_id: str, learner_id: str):
        session = await self.repo.get_session_detail(session_id, learner_id)

        if not session:
            raise ValueError("Session not found")

        return session

    async def search_sessions(
        self,
        query: SessionSearchQuery,
    ):
        sessions, total = await self.repo.search_sessions(query)

        return {
            "items": sessions,
            "page": query.page,
            "page_size": query.page_size,
            "total": total,
        }

    async def submit_interaction_stream(
        self,
        learner_id,
        session_id,
        task_id,
        interaction,
        answer,
    ):
        # get the current task to see the type

        # Session
        session = await self.session_repo.get_full_session(session_id)
        if not session:
            raise ValueError("Session not found")

        # Activity
        activity = await self.activity_repo.get_by_id(session.activity_id)

        # Task
        task = activity.tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")

        task_type = task.type

        if task_type == TaskType.GENERATE:
            # handle generate type
            async for token in self.orchestrator.stream_flow(
                learner_id=learner_id,
                session_id=session_id,
                task_id=task_id,
                interaction=interaction,
                answer=answer,
            ):
                yield token
        else:
            None

    async def submit_interaction(
        self,
        learner_id,
        session_id,
        task_id,
        interaction,
        answer,
    ):
        interaction = await self.orchestrator.flow(
            learner_id=learner_id,
            session_id=session_id,
            task_id=task_id,
            interaction=interaction,
            answer=answer,
        )

        return interaction

    async def get_current_task(self, session_id: str) -> Dict[str, Any]:

        session = await self.session_repo.get_with_progress(session_id)

        if not session:
            raise ValueError("Session not found")

        activity = await self.activity_repo.get_by_id(session.activity_id)

        if not activity:
            raise ValueError("Activity not found")

        # current task
        current_task_id = session.current_task

        # get task from activity
        task = activity.tasks.get(current_task_id)

        if not task:
            raise ValueError("Task not found in activity")

        #
        progress = next(
            (p for p in session.progresses if p.task_id == current_task_id),
            None,
        )

        #
        last_interaction = None
        if progress and progress.interactions:
            last = progress.interactions[-1]
            last_interaction = {
                "attempt": last.attempt,
                "is_correct": last.is_correct,
                "score": last.score,
            }

        # final
        return {
            "session": {
                "id": str(session.id),
                "status": session.status,
                "progress": session.progress,
                "score": session.score,
            },
            "task": task.dict(),
            "progress": {
                "status": progress.status if progress else None,
                "num_attempts": progress.num_attempts if progress else 0,
                "score": progress.score if progress else None,
            },
            "interaction": last_interaction,
        }

    async def create_session_from_activity(
        self,
        activity_id: str,
        learner_id: str,
    ) -> Session:

        # FIXME: Remember to also create the conversation inside the session
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

        # Build all progresses
        session.progresses = self._build_progress(
            activity,
            session_id,
            start_task_id,
        )

        # create the embedded conversation
        conversation = self._build_conversation(learner_id, activity)
        session.conversation = conversation

        # persist the session
        return await self.session_repo.create(session)

    def _build_conversation(
        self,
        learner_id: str,
        activity,
    ) -> Conversation:
        return Conversation(
            learner_id=learner_id,
            type="EMBEDDED",
            title=f"Session for {activity.metadata.title}",
        )

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

    # FIXME:
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

    # FIXME:
    async def get_current_goal(self, session_id):
        session = self.session_repo.get_session_by_id(session_id)
        activity_id = session["activity_id"]
        goal_id = session["current_goal"]
        goal = self.activity_repo.get_goal_by_id(
            activity_id=activity_id,
            goal_id=goal_id,
        )
        return goal, session["status"]

    # FIXME:
    def new_session(self, learner_id: str, activity_id: str):
        con_id = self.con_repo.create_new_conversation(type="EMBEDDED")

        session = self.session_repo.create_session(
            activity_id,
            con_id,
        )

        return session
