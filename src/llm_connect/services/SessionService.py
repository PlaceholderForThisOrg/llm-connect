from llm_connect import logger
from llm_connect.services.immerse.Orchestrator import Orchestrator


class SessionService:
    def __init__(self, orchestrator: Orchestrator):
        self.o = orchestrator

    async def handle_interact(self, session_id: str, content: str):
        logger.info("🤔 Service")
        yield content
