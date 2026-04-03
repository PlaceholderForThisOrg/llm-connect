import time

from fastapi import BackgroundTasks
from openai import AsyncOpenAI
from redis.asyncio import Redis

from llm_connect.configs.llm import GPT41
from llm_connect.configs.redis import MESSAGE_STREAM
from llm_connect.models.MessageStream import MessageStream, Role
from llm_connect.services.immerse import Orchestrator


class ChatService:
    def __init__(self, llm: AsyncOpenAI, redis: Redis, orchestrator: Orchestrator):
        self.llm = llm
        self.redis = redis
        self.orchestrator = orchestrator

    async def stream(self, message: str, user_id: str):
        async with self.llm.chat.completions.stream(
            model=GPT41,
            messages=[{"role": "user", "content": message}],
        ) as stream:
            async for event in stream:
                if event.type == "content.delta":
                    yield event.delta
                elif event.type == "content.done":
                    yield "[DONE]"

    async def push_message(self, content: str, user_id: str, role: Role):
        message = MessageStream(
            user_id=user_id,
            role=str(role),
            content=content,
            timestamp=str(int(time.time() * 1000)),
        )

        await self.redis.xadd(MESSAGE_STREAM, fields=message.model_dump())

    async def scenario_immerse(
        self,
        input: str,
        scenario_id: int,
        engine: BackgroundTasks,
    ):
        async for token in self.orchestrator.start(
            scenario_id,
            input,
            engine,
        ):
            yield token
