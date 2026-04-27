from pathlib import Path
from typing import Dict, List, TypedDict

from jinja2 import Environment, FileSystemLoader

from llm_connect.proto.scenario import scenario, scenario_template


class MoveCheckpointParams(TypedDict):
    checkpoint_name: str
    checkpoint_description: str
    transition_condition: str
    history: str
    user_input: str


class ReInteractParams(TypedDict):
    npc_name: str
    npc_role: str
    npc_personality: str
    scenario_description: str
    scene_location: str
    scene_goal: str
    conversation_history: str
    learner_message: str


class GoalEvaluateParams(TypedDict):
    goal: str
    learner_input: str


class NPCParams(TypedDict):
    learner_interaction: str
    finished_goal: str
    next_goal: str


class CompanionParams(TypedDict):
    user_memory: str = None
    history: List
    input: str


class CompanionHelpParams(TypedDict):
    activity: str
    goal: str
    latest_attempt: str
    result: str
    history: Dict
    knowledge: str
    type: str


class PromptBuilder:
    def __init__(self):
        PROMPT = Path(__file__).resolve().parent.parent.parent / "prompt"
        loader = FileSystemLoader(
            searchpath=[PROMPT / "evaluator", PROMPT / "actor", PROMPT]
        )

        self.env = Environment(loader=loader)

    def companion_help_prompt(
        self,
        params: CompanionHelpParams,
    ):
        template = self.env.get_template(name="companion_help.jinja")
        return template.render(**params)

    def companion_prompt(
        self,
        params: CompanionParams,
    ):
        template = self.env.get_template(name="companion.jinja")
        return template.render(**params)

    def npc(
        self,
        params: NPCParams,
    ):
        template = self.env.get_template(name="npc.jinja")
        return template.render(**params)

    def goal_evaluate(
        self,
        params: GoalEvaluateParams,
    ):
        template = self.env.get_template(name="goal_evaluate_v1.jinja")
        return template.render(**params)

    def move_checkpoint(
        self,
        params: MoveCheckpointParams,
    ):
        template = self.env.get_template(name="change_state.jinja")
        return template.render(**params)

    def re_interact(
        self,
        params: ReInteractParams,
    ):
        template = self.env.get_template(name="response.jinja")
        return template.render(**params)

    # FIXME: Delete this
    def intention_prompt(
        self,
        scenario_id: int,
        input: str,
    ) -> str:
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
