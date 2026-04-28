import json
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from llm_connect.configs.llm import GPT4OMINI, GPT41
from llm_connect.services.immerse.PromptBuilder import (
    GoalEvaluateParams,
    NPCParams,
    PromptBuilder,
)


class TaskManager(ABC):
    @abstractmethod
    async def evaluate(self, activity_id, task, interactions):
        None

    async def update_mastery(
        self,
        learner_id,
        activity_id,
        task_id,
        result,
        atomic_point_id,
    ):
        None

    @abstractmethod
    async def response(
        self,
        activity_id,
        task,
        next_task,
        result,
        interactions,
    ):
        None


class SelectTaskManager(TaskManager):
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        client: AsyncOpenAI,
    ):
        super().__init__()
        self.pb = prompt_builder
        self.llm_client = client

    async def evaluate(self, activity_id: str, task_id: str, interactions: str):
        None


class GenerateTaskManager(TaskManager):
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        client: AsyncOpenAI,
    ):
        super().__init__()
        self.pb = prompt_builder
        self.client = client

    async def evaluate(self, activity_id, task, interactions) -> bool:
        params = GoalEvaluateParams(goal=task.prompt, learner_input=interactions)

        prompt = self.pb.goal_evaluate(params=params)

        # Call the LLM for evaluation
        response = await self.client.chat.completions.create(
            model=GPT4OMINI,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        result = response.choices[0].message.content
        result = json.loads(result)
        result = result["result"]
        return result

    async def response(
        self,
        activity_id,
        task,
        next_task,
        result,
        interactions,
    ):
        if result is False:
            # FIXME: change to prompt
            yield "I don't understand what you are saying!"

        else:
            params = NPCParams(
                learner_interaction=interactions,
                finished_goal=task.prompt,
                next_goal=next_task.prompt,
            )

            prompt = self.pb.npc(params)

            async with self.client.chat.completions.stream(
                model=GPT41, messages=[{"role": "user", "content": prompt}]
            ) as stream_manager:
                async for event in stream_manager:
                    if event.type == "content.delta":
                        yield event.delta
