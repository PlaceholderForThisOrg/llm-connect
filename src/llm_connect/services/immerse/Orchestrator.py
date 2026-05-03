import asyncio
import random
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect import logger
from llm_connect.configs import gpt41_semaphore
from llm_connect.models import Interaction
from llm_connect.models.Activity import TaskType
from llm_connect.models.Session import Session
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.InteractionRepository import InteractionRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.analyzer.Analyzer import Analyzer
from llm_connect.services.core.aevaluator import AEvaluator
from llm_connect.services.core.MasteryEngine import MasteryEngine
from llm_connect.services.core.RolePlaySessionManager import RolePlaySessionManager
from llm_connect.services.core.TaskManager import (
    FillTaskManager,
    GenerateTaskManager,
    MatchTaskManager,
    ReorderTaskManager,
    SelectTaskManager,
    TaskManager,
)
from llm_connect.services.immerse import Actor, Evaluator, PromptBuilder


class SessionStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ProgressStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Orchestrator:
    def __init__(
        self,
        evaluator: Evaluator,
        actor: Actor,
        prompt_builder: PromptBuilder,
        analyzer: Analyzer,
        aevaluator: AEvaluator,
        session_manager: RolePlaySessionManager,
        session_repo: SessionRepository,
        activity_repo: ActivityRepository,
        l_repo: LearnerRepository,
        task_manager: TaskManager,
        mastery_engine: MasteryEngine,
        session: AsyncSession,
        select_manager: SelectTaskManager,
        fill_manager: FillTaskManager,
        match_manager: MatchTaskManager,
        reorder_manager: ReorderTaskManager,
        generate_manager: GenerateTaskManager,
        interaction_repo: InteractionRepository,
    ):
        self.evaluator = evaluator
        self.actor = actor
        self.prompt_builder = prompt_builder
        self.analyzer = analyzer
        self.aevaluator = aevaluator
        self.session_manager = session_manager
        self.session_repo = session_repo
        self.activity_repo = activity_repo
        self.l_repo = l_repo
        self.task_manager = task_manager
        self.mastery_engine = mastery_engine
        self.session = session
        self.select_manager = select_manager
        self.fill_manager = fill_manager
        self.match_manager = match_manager
        self.reorder_manager = reorder_manager
        self.generate_manager = generate_manager
        self.interaction_repo = interaction_repo

    def _compute_progress(self, session: Session) -> float:
        total = len(session.progresses)
        completed = sum(1 for p in session.progresses if p.status == "COMPLETED")
        return completed / total if total > 0 else 0.0

    def _compute_score(self, session) -> Optional[float]:
        scores = [p.score for p in session.progresses if p.score is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)

    async def stream_flow(
        self,
        learner_id: str,
        session_id: str,
        task_id: str,
        interaction,
        answer,
    ):
        # is_final = False
        logger.info("- Load metadata")

        # Session
        session = await self.session_repo.get_full_session(session_id)
        if not session:
            raise ValueError("Session not found")

        # Activity
        activity = await self.activity_repo.get_by_id(session.activity_id)
        # activity_type = activity.metadata.type
        if not activity:
            raise ValueError("Activity not found")

        # Task
        task = activity.tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")

        # Atomic point IDs
        ap_ids = task.atomic_points

        # Next possible tasks
        # FIXME: ALways choose the first one

        if len(task.next_possibles) == 0:
            # That is the final task
            # is_final = True
            next_task_id = None
            next_task = None

        else:
            next_task_id = random.sample(population=task.next_possibles, k=1)[0]
            next_task = activity.tasks.get(next_task_id, None)

        # next_task_id = task.next_possibles[0] if len(task.next_possibles) > 0 else None
        # next_task = activity.tasks.get(next_task_id, None)

        # Current progress
        progress = next(
            (p for p in session.progresses if p.task_id == task_id),
            None,
        )

        next_progress = next(
            (p for p in session.progresses if p.task_id == next_task_id), None
        )

        if not progress:
            raise ValueError("Progress not found")

        # Increase attempt
        attempt = (progress.num_attempts or 0) + 1
        progress.num_attempts = attempt
        now = datetime.now(timezone.utc)

        # Start at logic
        if progress.started_at is None:
            progress.started_at = now

        logger.info("- Core evaluation")

        response = ""

        logger.info(f"------- Current task's type is {task.type}")

        # result = await self.task_manager.evaluate(
        #     activity_id=activity.id,
        #     task=task,
        #     interactions=answer.response,
        # )

        history = await self.interaction_repo.get_session_history(session_id=session.id)

        result = await self.generate_manager.evaluatev2(
            context=activity.metadata.description,
            task=task,
            interactions=answer.response,
            learner_input=answer.response,
            history=history,
        )

        await asyncio.sleep(0)

        logger.info(f"Can the learner move to the next task {result}")

        # MASTERY UPDATE
        logger.info("[3] --- Core mastery update")

        logger.info(f"Atomic points: {ap_ids}")

        await self.mastery_engine.update_v2(
            result=result,
            learner_id=learner_id,
            ap_ids=ap_ids,
        )

        # Response the system
        # next_task can be None

        async with gpt41_semaphore:
            async for token in self.generate_manager.responsev2(
                activity_id=activity.id,
                task=task,
                next_task=next_task,
                result=result,
                interactions=answer.response,
                history=history,
                activity=activity,
            ):
                response += token
                yield token

        # Update Session
        logger.info("[4] --- Update session")

        interaction = Interaction(
            id=uuid.uuid4(),
            progress_id=progress.id,
            attempt=attempt,
            input=answer.response,
            output=response,
            is_correct=result,
            score=1.0 if result else random.uniform(0, 1.0),
            created_at=now,
            meta="{}",
        )

        # update progress
        # calculate progress
        score_progress = self._compute_progress(session)
        session.progress = score_progress

        # add interaction
        progress.interactions.append(interaction)
        progress.num_attempts = attempt

        # Correct result -> Finish task
        # Wrong result -> Don't finish
        if result:
            # current progress is finished
            progress.status = "COMPLETED"
            progress.completed_at = now
        else:
            progress.status = "IN_PROGRESS"

        # Moving
        if progress.status == "COMPLETED":
            # Redo a task -> Move to the next task

            # Move to the next task
            if next_progress and next_progress.status == "LOCKED":
                session.current_task = next_task_id
                next_progress.status = "UNLOCKED"

            else:
                # Session is completed
                logger.info("Session is done!")
                session.status = "COMPLETED"
                session.completed_at = now

        else:
            # Don't move
            None

        await self.session.commit()

    async def flow(
        self,
        learner_id: str,
        session_id: str,
        task_id: str,
        interaction,
        answer,
    ):
        logger.info("[1] --- Load metadata")
        # Session
        session = await self.session_repo.get_full_session(session_id)
        if not session:
            raise ValueError("Session not found")

        # Activity
        activity = await self.activity_repo.get_by_id(session.activity_id)
        # activity_type = activity.metadata.type
        if not activity:
            raise ValueError("Activity not found")

        # Task
        task = activity.tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")
        # task_type = task.type
        ap_ids = task.atomic_points
        task_type = task.type

        # Next possible tasks
        # FIXME: ALways choose the second
        if len(task.next_possibles) == 0:
            # That is the final task
            # is_final = True
            next_task_id = None
            # next_task = None

        else:
            next_task_id = random.sample(population=task.next_possibles, k=1)[0]
            # next_task = activity.tasks.get(next_task_id, None)

        # Current progress
        progress = next(
            (p for p in session.progresses if p.task_id == task_id),
            None,
        )

        next_progress = next(
            (p for p in session.progresses if p.task_id == next_task_id), None
        )

        if not progress:
            raise ValueError("Progress not found")

        attempt = (progress.num_attempts or 0) + 1
        now = datetime.now(timezone.utc)

        if progress.started_at is None:
            progress.started_at = now

        # Evaluation
        if task_type == TaskType.SELECT:

            input = answer.response

            result = await self.select_manager.evaluate(
                interactions=answer,
                task=task,
            )
            score = 1.0 if result is True else 0.0

            response = await self.select_manager.response(
                result=result,
            )

        elif task_type == TaskType.FILL:
            logger.info("Task is fill")

            input = answer.response

            result, score = await self.fill_manager.evaluate(
                answer,
                task=task,
            )

            # progress.score = score

            response = await self.fill_manager.response(result)

        elif task_type == TaskType.MATCH:
            input = answer.response

            result, score = await self.match_manager.evaluate(
                interactions=answer, task=task
            )

            # progress.score = score

            response = await self.match_manager.response(result)

        elif task_type == TaskType.REORDER:
            input = answer.response

            result, score = await self.reorder_manager.evaluate(
                interactions=answer, task=task
            )

            # progress.score = score

            response = await self.reorder_manager.response(result=result)

        else:
            # fallback
            result = False
            response = ""

            # MASTERY UPDATE
        logger.info("[3] --- Core mastery update")

        await self.mastery_engine.update_v2(
            result=result,
            learner_id=learner_id,
            ap_ids=ap_ids,
        )

        # Update Session
        logger.info("[4] --- Update session")

        interaction = Interaction(
            id=uuid.uuid4(),
            progress_id=progress.id,
            attempt=attempt,
            input=input,
            output=response,
            is_correct=result,
            score=score,
            created_at=now,
            meta="{}",
        )

        # update progress
        # calculate progress
        score_progress = self._compute_progress(session)
        session.progress = score_progress

        # add interaction
        progress.interactions.append(interaction)
        progress.num_attempts = attempt

        # Correct result -> Finish task
        # Wrong result -> Don't finish
        if result:
            # current progress is finished
            progress.status = "COMPLETED"
            progress.completed_at = now
        else:
            progress.status = "IN_PROGRESS"

        # Moving
        if progress.status == "COMPLETED":
            # Redo a task -> Move to the next task

            # Move to the next task
            if next_progress and next_progress.status == "LOCKED":
                session.current_task = next_task_id
                next_progress.status = "UNLOCKED"

            else:
                # Session is completed
                logger.info("Session is done!")
                session.status = "COMPLETED"
                session.completed_at = now

        else:
            # Don't move
            None

        await self.session.commit()

        return {
            "id": interaction.id,
            "progress_id": progress.id,
            "attempt": attempt,
            "input": input,
            "output": response,
            "is_correct": result,
            "score": 0.0,
            "created_at": now,
            "meta": {},
        }

        # compute the progress
        # compute the score
        # Orchestrate on the interaction

    # FIXME:
    async def start(
        self,
        learner_id: str,
        session_id: str,
        content: str,
        engine: BackgroundTasks,
    ):

        # FIXME: Prototype

        logger.info("1️⃣  Orchestration started!")

        logger.info("📊  Load the session and the activity")
        session = self.session_repo.get_session_by_id(session_id)
        activity_id = session["activity_id"]
        activity = self.activity_repo.get_activity_by_id(activity_id)

        learner = self.l_repo.get_by_id(learner_id)

        logger.info("2️⃣  Interaction object created!")

        logger.info("3️⃣  Evaluation started")
        self.aevaluator.run(input, engine)

        async for token in self.session_manager.accept(
            learner,
            session,
            activity,
            content,
        ):
            yield token
