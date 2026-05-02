import json
import random
from abc import ABC, abstractmethod
from ast import List

from openai import AsyncOpenAI

from llm_connect.configs.llm import GPT4OMINI, GPT41
from llm_connect.models.Activity import (
    Activity,
    FillTask,
    GenerateTask,
    MatchTask,
    ReorderTask,
    SelectTask,
)
from llm_connect.schemas.session_schema import (
    FillAnswer,
    MatchAnswer,
    ReorderAnswer,
    SelectAnswer,
)
from llm_connect.services.immerse.PromptBuilder import (
    GoalEvaluateParams,
    GoalEvaluateParamsv2,
    NPCParams,
    NPCParamsv2,
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


class MatchTaskManager(TaskManager):
    def __init__(self):
        super().__init__()

    async def evaluate(
        self,
        interactions: MatchAnswer,
        task: MatchTask,
    ):
        correct_pairs = task.correct_pairs
        answers = interactions.response

        corrects = 0

        for key, value in answers.items():
            if key in correct_pairs and correct_pairs[key] == value:
                corrects += 1

        # result
        result = corrects == len(correct_pairs) == len(answers)

        score = corrects / len(correct_pairs) if correct_pairs else 0

        return result, score

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


class ReorderTaskManager(TaskManager):
    def __init__(
        self,
    ):
        super().__init__()

    async def evaluate(
        self,
        interactions: ReorderAnswer,
        task: ReorderTask,
    ):
        correct_order = task.correct_orders
        answers = interactions.response

        corrects = 0

        # Compare position by position
        for i, value in enumerate(answers):
            if i < len(correct_order) and value == correct_order[i]:
                corrects += 1

        # Fully correct only if everything matches and lengths are equal
        result = answers == correct_order

        score = corrects / len(correct_order) if correct_order else 0

        return result, score

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
        answers = [str.lower(a) for a in interactions.response]

        corrects = 0
        result = True

        for answer, correct in zip(answers, correct_answers):
            if answer == correct:
                corrects += 1
            else:
                result = False

        score = corrects / len(answers) if answers else 0
        return result, score

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
        answers = interactions.response

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

    async def evaluatev2(
        self,
        context,
        task: GenerateTask,
        history,
        interactions,
        learner_input,
    ) -> bool:
        # params = GoalEvaluateParams(goal=task.prompt, learner_input=interactions)
        params = GoalEvaluateParamsv2(
            context=context,
            history=history,
            learner_input=interactions,
            criteria=None,
            goal=task.prompt,
        )

        prompt = self.pb.goal_evaluatev2(params=params)

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

    async def responsev2(
        self,
        activity_id,
        task: GenerateTask,
        next_task: GenerateTask,
        result,
        interactions,
        activity: Activity,
        history: List,
    ):
        params = NPCParamsv2(
            context=activity.metadata.description,
            npc=activity.metadata.npc,
            current_task=task.prompt,
            result=result,
            next_task=next_task.prompt if next_task else "No task left",
            history=history,
            learner_input=interactions,
        )

        prompt = self.pb.npcv2(params)

        async with self.client.chat.completions.stream(
            model=GPT41, messages=[{"role": "user", "content": prompt}]
        ) as stream_manager:
            async for event in stream_manager:
                if event.type == "content.delta":
                    yield event.delta

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
            finished_goal = task.prompt
            next_goal = next_task.prompt if next_task else "No further task any more"

            params = NPCParams(
                learner_interaction=interactions,
                finished_goal=finished_goal,
                next_goal=next_goal,
            )

            prompt = self.pb.npc(params)

            async with self.client.chat.completions.stream(
                model=GPT41, messages=[{"role": "user", "content": prompt}]
            ) as stream_manager:
                async for event in stream_manager:
                    if event.type == "content.delta":
                        yield event.delta
