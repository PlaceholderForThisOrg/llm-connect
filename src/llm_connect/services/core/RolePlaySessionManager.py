# FIXME: Remember to fix this logic
import json
import random
from datetime import datetime, timezone

from openai import AsyncOpenAI

from llm_connect import logger
from llm_connect.configs.llm import GPT4OMINI, GPT41
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.core.SessionManager import SessionManager
from llm_connect.services.immerse import PromptBuilder
from llm_connect.services.immerse.PromptBuilder import (
    GoalEvaluateParams,
    MoveCheckpointParams,
    NPCParams,
    ReInteractParams,
)


# NOTE: It belongs to the activity, only check
# for the actiivty itself
class RolePlaySessionManager(SessionManager):
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        client: AsyncOpenAI,
        session_repo: SessionRepository,
    ):
        super().__init__()
        self.prompt_builder = prompt_builder
        self.client = client
        self.session_repo = session_repo

    async def accept(self, session, activity, interaction):

        # store the interaction first
        self.append_interaction(
            session,
            activity,
            of="LEARNER",
            content=interaction,
        )

        # Check the interaction against the current goal
        goal_id = session["current_goal"]
        goal = activity["goals"][goal_id]

        raw_goal = goal["goal"]

        # Use LLM for checking

        goal_evaluate_params: GoalEvaluateParams = GoalEvaluateParams(
            goal=raw_goal, learner_input=interaction
        )

        prompt = self.prompt_builder.goal_evaluate(params=goal_evaluate_params)

        result = await self._use_brain(prompt)
        if result:
            # OK -> move the pointer to the next goal
            # Generate the reponse
            # Don't save the interaction by now
            # This is just a prototype

            # get the next pointer
            next_possible_goal_ids = goal["next_possibles"]
            if len(next_possible_goal_ids) == 0:
                session["current_goal"] = "-1"
                session["status"] = "DONE"
                yield "終わったよよくがんばってね。"
            else:

                next_goal_id = random.choice(next_possible_goal_ids)

                # advance the pointer to the next goal
                session["current_goal"] = next_goal_id
                next_goal = activity["goals"][next_goal_id]["goal"]

                # Now build the prompt for the NPC
                # to response and optional link the new goal
                npc_params = NPCParams(
                    learner_interaction=interaction,
                    finished_goal=goal["goal"],
                    next_goal=next_goal,
                )

                prompt = self.prompt_builder.npc(npc_params)

                # Now ask the LLM to generate the response
                # for the learner

                response = ""

                async with self.client.chat.completions.stream(
                    model=GPT41, messages=[{"role": "user", "content": prompt}]
                ) as stream_manager:
                    async for event in stream_manager:
                        if event.type == "content.delta":
                            response += event.delta
                            yield event.delta

                        if event.type == "content.done":
                            # Store the response into scenario
                            self.append_interaction(
                                session,
                                activity,
                                of="NPC",
                                content=response,
                            )
                            yield "_🙆‍♂️_"
        else:
            # Not OK
            # Then based on the current goal
            # don't move the pointer
            # the learner is still there
            # companion comes in
            response = "What is hell is going on?"
            self.append_interaction(
                session,
                activity,
                of="NPC",
                content=response,
            )
            yield response

    async def evaluate(self, interaction) -> bool:
        None

    def is_final(self, session, activity):
        curr_checkpoint = session["checkpoint"]

        return (
            True if activity["checkpoints"][curr_checkpoint]["next"] is None else False
        )

    async def update(
        self,
        session,
        activity,
        content: str,
    ):
        if await self.can_move(
            "1",
            content,
            session,
            activity,
        ):
            # TODO: Update the session into the next checkpoint

            # TODO: If the final checkpoint is done
            if self.is_final(session, activity):
                pass
            else:
                # move to the next checkpoint
                curr_checkpoint = session["checkpoint"]
                next_checkpoint = activity["checkpoints"][curr_checkpoint]["next"]
                self.session_repo.update_next_checkpoint("1", next_checkpoint)
        else:
            pass

    async def can_move(
        self,
        session_id: str,
        content: str,
        session,  # get from the orchestrator
        activity,  # get from the orchestrator
    ) -> bool:
        # FIXME: Implement whether the learner can move
        # to the next checkpoints
        # [v1]: Only check the task finish
        # [v2]: Aggregate the atomic points completion

        # Logic
        # session and activity is provided by the orchestrator
        curr_checkpoint_id = session["checkpoint"]
        checkpoint = activity["checkpoints"][curr_checkpoint_id]

        # Create the history
        history = session["history"]
        hist = [
            f"{interaction["of"]}: {interaction["content"]}" for interaction in history
        ]
        hist = "\n".join(hist)

        latest = history[-1]["content"]

        params: MoveCheckpointParams = MoveCheckpointParams(
            checkpoint_name=checkpoint["name"],
            checkpoint_description=checkpoint["scene_context"],
            transition_condition=checkpoint["ends_when"],
            history=hist,
            user_input=latest,
        )

        prompt = self.prompt_builder.move_checkpoint(params)

        result = await self._use_brain(prompt)

        logger.info(f"😍  Should the learner moves: {result}")

        return result

    async def move(self):
        pass

    async def re_interact(self, session, activity, content):
        curr_checkpoint = session["checkpoint"]
        checkpoint = activity["checkpoints"][curr_checkpoint]
        meta = activity["metadata"]

        history = session["history"]
        hist = [
            f"{interaction["of"]}: {interaction["content"]}" for interaction in history
        ]
        hist = "\n".join(hist)
        latest = history[-1]["content"]

        params: ReInteractParams = ReInteractParams(
            npc_name=meta["npc_name"],
            npc_role=meta["npc_role"],
            npc_personality=meta["npc_personality"],
            scenario_description=activity["description"],
            scene_location=activity["context"],
            scene_goal=checkpoint["learner_goal"],
            conversation_history=hist,
            learner_message=latest,
        )

        response = ""
        prompt = self.prompt_builder.re_interact(params)

        async with self.client.chat.completions.stream(
            model=GPT41, messages=[{"role": "user", "content": prompt}]
        ) as stream_manager:
            async for event in stream_manager:
                if event.type == "content.delta":
                    response += event.delta
                    yield event.delta

                if event.type == "content.done":
                    # Store the response into scenario
                    self.append_interaction(
                        session,
                        activity,
                        of="NPC",
                        content=response,
                    )
                    yield "_🙆‍♂️_"

    def append_interaction(self, session, activity, of: str, content):
        timestamp = datetime.now(timezone.utc).timestamp()

        session_id = "session_002"

        interaction = {
            "id": "0",
            "type": "MESSAGE",
            "of": of,
            "content": content,
            "timestamp": timestamp,
        }

        self.session_repo.add_interaction(session_id, interaction)

    async def _use_brain(self, prompt: str) -> bool:
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
        return result["result"]
