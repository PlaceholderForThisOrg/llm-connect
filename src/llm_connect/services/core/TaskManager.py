import json
import random
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from llm_connect.configs.llm import GPT4OMINI, GPT41
from llm_connect.models.Activity import FillTask, SelectTask
from llm_connect.schemas.session_schema import FillAnswer, SelectAnswer
from llm_connect.services.immerse.PromptBuilder import (
    GoalEvaluateParams,
    NPCParams,
    PromptBuilder,
)

RESPONSES_IF_CORRECT = [
    "Great job!",
    "Exellent!",
    "Fantastic!",
]

RESPONSES_IF_INCORRECT = [
    "Try again!",
    "It's not true!",
    "Try a new answer!",
]


class TaskManager(ABC):
    @abstractmethod
    async def evaluate(
        self,
        activity_id,
        task,
        interactions,
    ):
        None

    # FIXME: This is for the Mastery Engine
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


class FillTaskManager(TaskManager):
    def __init__(
        self,
    ):
        super().__init__()

    async def evaluate(
        self,
        interactions: FillAnswer,
        task: FillTask,
    ):
        correct_answers = [str.lower(a) for a in task.correct_answers]
        answers = [str.lower(a) for a in interactions.filled]

        corrects = 0
        result = True

        for index, answer in enumerate(answers):
            if answer == correct_answers[index]:
                corrects += 1
                result = result and True

            else:
                result = result and False

        return result, corrects / len(answers)

    async def response(
        self,
        result,
    ):
        # Return the comments on whether or not
        # the current task is correct ot not
        # based on the result values
        if result:
            return random.sample(RESPONSES_IF_CORRECT, k=1)[0]

        else:
            return random.sample(RESPONSES_IF_INCORRECT, k=1)[0]


class SelectTaskManager(TaskManager):
    def __init__(
        self,
        # prompt_builder: PromptBuilder,
        # client: AsyncOpenAI,
    ):
        super().__init__()
        # self.pb = prompt_builder
        # self.llm_client = client

    async def evaluate(
        self,
        interactions: SelectAnswer,
        task: SelectTask,
    ):
        correct_options = task.correct_options
        answers = interactions.selected

        # normalize corrects and answers
        correct_set = set(correct_options)
        answer_set = set(answers)

        # check exact
        result = correct_set == answer_set

        return result

    async def response(
        self,
        result,
    ):
        # Return the comments on whether or not
        # the current task is correct ot not
        # based on the result values
        if result:
            return random.sample(RESPONSES_IF_CORRECT, k=1)[0]

        else:
            return random.sample(RESPONSES_IF_INCORRECT, k=1)[0]


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
