from pathlib import Path
from typing import TypedDict

from jinja2 import Environment, FileSystemLoader

from llm_connect.proto.scenario import scenario, scenario_template


class MoveCheckpointParams(TypedDict):
    checkpoint_name: str
    checkpoint_description: str
    transition_condition: str
    history: str
    user_input: str


class PromptBuilder:
    def __init__(self):
        PROMPT = Path(__file__).resolve().parent.parent.parent / "prompt"
        loader = FileSystemLoader(searchpath=[PROMPT / "evaluator", PROMPT / "actor"])

        self.env = Environment(loader=loader)

    def move_checkpoint(self, params: MoveCheckpointParams):
        template = self.env.get_template(name="change_state.jinja")
        return template.render(**params)

    def intention_prompt(self, scenario_id: int, input: str) -> str:
        # FIXME: The prompt builder should load the template and inject

        # scenario_id is used as the reference to get the status to
        # create the prompt

        template = self.env.get_template(name="change_state.jinja")
        # from scenario_id -> current state
        current_index = scenario["index"]

        # from scenario_id -> template -> get current goal

        goal = scenario_template["states"][current_index]["goal"]
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
