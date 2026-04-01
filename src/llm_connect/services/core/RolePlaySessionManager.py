# FIXME: Remember to fix this logic
import json
from datetime import datetime, timezone

from openai import AsyncOpenAI

from llm_connect import logger
from llm_connect.configs.llm import GPT4OMINI, GPT41
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.core.SessionManager import SessionManager
from llm_connect.services.immerse import PromptBuilder
from llm_connect.services.immerse.PromptBuilder import (
    MoveCheckpointParams,
    ReInteractParams,
)


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
        interaction = {
            "id": "0",
            "type": "MESSAGE",
            "of": of,
            "content": content,
            "timestamp": timestamp,
        }
        session["history"].append(interaction)

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
