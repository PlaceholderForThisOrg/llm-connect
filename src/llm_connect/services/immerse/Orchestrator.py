from fastapi import BackgroundTasks

from llm_connect import logger
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.analyzer.Analyzer import Analyzer
from llm_connect.services.core.aevaluator import AEvaluator
from llm_connect.services.core.RolePlaySessionManager import RolePlaySessionManager
from llm_connect.services.immerse import Actor, Evaluator, PromptBuilder


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

    # Orchestrate on the interaction
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
