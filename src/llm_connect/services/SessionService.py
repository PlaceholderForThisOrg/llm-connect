from fastapi import BackgroundTasks

from llm_connect import logger
from llm_connect.services.immerse.Orchestrator import Orchestrator


class SessionService:
    def __init__(self, orchestrator: Orchestrator):
        self.o = orchestrator

    async def handle_interact(
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

        yield "🤏"
