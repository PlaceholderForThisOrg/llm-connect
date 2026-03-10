import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI
from redis.asyncio import Redis

from llm_connect.configs.llm import GPT41
from llm_connect.configs.redis import MESSAGE_STREAM
from llm_connect.models.MessageStream import MessageStream, Role


class ChatService:
    def __init__(
        self,
        llm: AsyncOpenAI,
        redis: Redis,
        orchestrator: Orchestrator,
    ):
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


class Orchestrator:
    def __init__(self, evaluator, prompt_builder):
        self.evaluator = evaluator
        self.prompt_builder = prompt_builder

    def orchestrate(self, input):
        # scenario_id = self.scenario["id"]
        # current_state = self.scenario["state"]

        self.prompt_builder.evaluate_intention()
        None


class Evaluator:
    def __init__(self):
        pass


class PromptBuilder:
    def __init__(self):
        PROMPT = Path(__file__).resolve().parent.parent / "prompt"
        loader = FileSystemLoader(searchpath=[PROMPT / "evaluator"])

        self.env = Environment(loader=loader)

    def evaluate_intention(self):
        template = self.env.get_template(name="change_state.jinja")
        print(template)
