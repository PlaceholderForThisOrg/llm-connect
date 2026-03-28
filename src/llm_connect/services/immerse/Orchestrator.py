from fastapi import BackgroundTasks

from llm_connect import logger
from llm_connect.proto.session import sync_session
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.analyzer.Analyzer import Analyzer
from llm_connect.services.core.aevaluator import AEvaluator
from llm_connect.services.core.SessionManager import RolePlaySessionManager
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
    ):
        self.evaluator = evaluator
        self.actor = actor
        self.prompt_builder = prompt_builder
        self.analyzer = analyzer
        self.aevaluator = aevaluator
        self.session_manager = session_manager
        self.session_repo = session_repo
        self.activity_repo = activity_repo

    # Orchestrate on the interaction
    async def start(
        self,
        scenario_id: int,
        content: str,
        engine: BackgroundTasks,
    ):

        # FIXME: Prototype
        logger.info("1️⃣  Orchestration started!")
        # TODO: The orchestrator is run on each interaction between
        # the learner and the system

        #
        logger.info("📊  Load the session and the activity")
        session = self.session_repo.get_session_by_id("1")
        activity = self.activity_repo.get_activity_by_id("activity_001")

        # TODO: Store the current interaction first
        # 1. Create the interaction object
        logger.info("2️⃣  Interaction object created!")
        self.session_manager.append_interaction(
            session,
            activity,
            of="LEARNER",
            content=content,
        )

        # TODO: Run the evaluator to extract the performance
        # on the expected atomic points
        # Optionally extract the errors in-place
        logger.info("3️⃣  Evaluation started")
        self.aevaluator.run(input, engine)

        # TODO: Now let's the session manager response
        async for token in self.session_manager.re_interact(
            session,
            activity,
            content,
        ):
            yield token

        # TODO: Session, check whether the current checkpoint
        # is good to move
        logger.info("✋  Session manager's checkpoint checking")
        await self.session_manager.update(session, activity, content)

        sync_session()
