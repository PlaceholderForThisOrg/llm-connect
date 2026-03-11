import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI
from redis.asyncio import Redis

from llm_connect.configs.llm import GPT4OMINI, GPT41
from llm_connect.configs.redis import MESSAGE_STREAM
from llm_connect.models.MessageStream import MessageStream, Role
from llm_connect.proto.scenario import scenario, scenario_template


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

    async def scenario_immerse(self, input: str, scenario_id: int):
        return await self.orchestrator.orchestrate(scenario_id, input)

        # return self.orchestrator.prompt_builder.evaluate_intention()


class Orchestrator:
    def __init__(
        self, evaluator: Evaluator, actor: Actor, prompt_builder: PromptBuilder
    ):
        self.evaluator = evaluator
        self.actor = actor
        self.prompt_builder = prompt_builder

    async def orchestrate(self, scenario_id: int, input: str):
        # [1] The orchestrator receives the message from the learner
        # store that message into the scenario object
        scenario["messages"].append({"role": "learner", "content": input})
        # [2] Use that message/history to ask for the current state from the evaluator
        # get the result
        # state = self.evaluator.next_state(input)

        # [2.1] Use the state to update the current state
        # if state == "true":
        #     # Move the scenario to the next state
        #     # check for the end state
        #     if scenario["index"] == len(scenario_template["states"]):
        #         # conversation has done
        #         return

        #     scenario["index"] += 1
        #     scenario["state"] = scenario_template["states"][scenario["index"]]["name"]

        # [3] Use that result to build the second prompt for the actor
        # send to the actor LLM
        return await self.actor.say(input)

        # [4] Stream the result back to the learner/store the message


class Evaluator:
    def __init__(self, client: AsyncOpenAI, prompt_builder: PromptBuilder):
        self.client = client
        self.prompt_builder = prompt_builder

    async def next_state(self, input: str) -> str:
        # [1] Build the prompt
        prompt = self.prompt_builder.evaluate_intention(1, input)
        response = await self.client.chat.completions.create(
            model=GPT4OMINI, messages=[{"role": "user", "content": prompt}]
        )

        state = response.choices[0].message.content
        return state


class Actor:
    def __init__(self, client: AsyncOpenAI, prompt_builder: PromptBuilder):
        self.client = client
        self.prompt_builder = prompt_builder

    async def say(self, input: str):
        prompt = self.prompt_builder.actor_prompt(1, input)
        return prompt


class PromptBuilder:
    def __init__(self):
        PROMPT = Path(__file__).resolve().parent.parent / "prompt"
        loader = FileSystemLoader(searchpath=[PROMPT / "evaluator", PROMPT / "actor"])

        self.env = Environment(loader=loader)

    def evaluate_intention(self, scenario_id: int, input: str) -> str:
        # scenario_id is used as the reference to get the status to
        # create the prompt

        template = self.env.get_template(name="change_state.jinja")
        # from scenario_id -> current state
        current_state = scenario["state"]
        # from scenario_id -> template -> get current goal
        goal = scenario_template["states"][current_state]["goal"]
        # create the conversation history
        messages = scenario["messages"]
        history = ""
        for record in messages:
            m = f"{record["role"]}:{record["content"]}"

            history += f"{m}\n"

        # get the latest user_input
        latest_message = input

        return template.render(
            state_name=scenario["state"],
            transition_condition=goal,
            conversation_history=history,
            user_input=latest_message,
        )

    def actor_prompt(self, scenario_id: int, input: str) -> str:
        template = self.env.get_template(name="final.jinja")

        state_index = scenario["index"]
        goal = scenario_template["states"][state_index]["goal"]

        # build the history's messages
        messages = scenario["messages"]
        history = ""
        for record in messages:
            m = f"{record["role"]}:{record["content"]}"

            history += f"{m}\n"

        return template.render(
            npc_name=scenario_template["character"]["name"],
            scenario_description=scenario_template["description"],
            scene_location=scenario_template["location"],
            npc_role=scenario_template["character"]["role"],
            npc_personality=scenario_template["character"]["personality"],
            scene_goal=goal,
            conversation_history=history,
            learner_message=input,
        )
