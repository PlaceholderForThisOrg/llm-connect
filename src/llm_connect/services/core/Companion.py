from typing import List
from uuid import UUID

from openai import AsyncOpenAI

from llm_connect import logger
from llm_connect.configs.llm import GPT41
from llm_connect.proto.atomic_points import ap2str
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.repositories.MessageRepository import MessageRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.immerse.PromptBuilder import (
    CompanionHelpParams,
    CompanionParams,
    CompanionSessionParams,
    PromptBuilder,
)


class Persionality:
    pass


class Knowledge:
    def __init__(
        self,
        ap_repo: AtomicPointRepository,
    ):
        self.ap_repo = ap_repo

    def get_aps(self, ids: List[str]):
        aps = [ap2str(self.ap_repo.get_atomic_point_by_id(id)) for id in ids]

        return "\n".join(aps)


class Brain:
    def __init__(self, llm: AsyncOpenAI):
        self.llm = llm

    async def think(self, prompt: str):
        async with self.llm.chat.completions.stream(
            model=GPT41, messages=[{"role": "user", "content": prompt}]
        ) as stream_manager:
            async for event in stream_manager:
                if event.type == "content.delta":
                    yield event.delta

    def make_decision(self, signals):
        # FIXME: Basic decision
        # later, more complex
        # based on different kinds of signals, ...
        # time, ...
        # Currently, check the retries
        p = signals["pass"]

        if p:
            # TODO:
            # Learner has pass
            # Still suggest help
            # But good cultural immerse, ...
            # Improve learning skill
            return "FREE"
        else:
            # Learner failed
            # Based on retries
            retries = signals["retries"]

            if retries == 1:
                # nudge
                return "NUDGE"
            elif retries == 2:
                # scafford
                return "SCAFFOLD"
            elif retries >= 3:
                # explaination
                return "EXPLANATION"


# NOTE: Memory and context together
class Memory:
    def __init__(
        self,
        learner_repo: LearnerRepository,
        con_repo: ConversationRepository,
        ses_repo: SessionRepository,
        ac_repo: ActivityRepository,
        message_repo: MessageRepository,
    ):
        self.long_term = learner_repo
        self.short_term = con_repo
        self.ses_repo = ses_repo
        self.ac_repo = ac_repo
        self.message_repo = message_repo

    async def current_activity(self, activity_id: str):
        activity = await self.ac_repo.get_by_id(activity_id)

        context = ""
        context += activity.metadata.type
        context += "\n"
        context += activity.metadata.title
        context += "\n"
        context += activity.metadata.description

        return context

    def longterm(self, learner_id: str):
        profile = self.long_term.get_by_id(learner_id)
        return profile["proto"]

    async def longterm_v2(self, learner_id: str):
        learner = await self.long_term.get_by_id(learner_id)
        return learner

    async def shortterm_v2(self, conversation_id: UUID):
        """Return the short-term memory for the companion

        Args:
            con_id (str): The conversation id
        """
        messages = await self.message_repo.get_conversation_messages(conversation_id)

        return messages

    def shortterm(self, con_id):
        con = self.short_term.get_conversation_by_id(con_id=con_id)
        messages = con["messages"]
        return messages

    def cur_sess(self, ses_id: str):
        return self.ses_repo.get_session_by_id(ses_id)

    def context(self, ses_id: str):
        # TODO: To return
        # the context of the session for the companion
        # to know
        pass


class Companion:
    def __init__(
        self,
        brain: Brain,
        memory: Memory,
        k: Knowledge,
        p: Persionality,
        pb: PromptBuilder,
    ):
        self.b = brain
        self.m = memory
        self.k = k
        self.p = p
        self.pb = pb
        self.memory = self.m
        self.brain = self.b

    # TODO: Emulate the companion role
    # need learner_id, the current con_id, the current message
    async def response_v2(
        self,
        learner_id: str,
        conversation_id: str,
        message: str,
        type: str,
        activity_id: str,
        session_id: str,
    ):
        if type == "NORMAL":
            logger.info("[Companion] - [Get the long-term memory]")
            # learner = await self.memory.longterm_v2(learner_id)

            logger.info("[Companion] - [Get the short-term memory]")
            messages = await self.memory.shortterm_v2(conversation_id)
            logger.info(f"[Companion] - [Short-term memory's length {len(messages)}]")

            # The companion's response

            # Build the companion prompt
            logger.info("[Companion] - [Build the prompt]")
            params = CompanionParams(
                # longterm
                user_memory="Currently not specified",
                # shortterm
                history=messages,
                input=message,
            )

            prompt = self.pb.companion_prompt(params)

            logger.info("[Companion] - [Yield the token from LLM]")

            async for token in self.brain.think(prompt):
                yield token
                # response += token
        elif type == "EMBEDDED":
            # inject the context
            logger.info("[Companion] - [Get the long-term memory]")
            # learner = await self.memory.longterm_v2(learner_id)

            logger.info("[Companion] - [Get the activity context]")
            context = await self.m.current_activity(activity_id)

            logger.info("[Companion] - [Get the short-term memory]")
            messages = await self.memory.shortterm_v2(conversation_id)
            logger.info(f"[Companion] - [Short-term memory's length {len(messages)}]")

            # The companion's response

            # Build the companion prompt
            logger.info("[Companion] - [Build the prompt]")
            params = CompanionSessionParams(
                user_memory="Currently not available",
                context=context,
                history=messages,
                input=message,
            )

            prompt = self.pb.companion_session_prompt(params)

            logger.info("[Companion] - [Yield the token from LLM]")
            async for token in self.brain.think(prompt):
                yield token
                # response += token

    async def response(self, learner_id: str, con_id: str, message: str):
        # TODO:
        # - Receive the learner
        # - The message
        # - The conversation
        # - Use the companion prompt template
        # - Fill in the things using components
        # - Ask the brain
        # - Stream the response back
        # FIXME: fix stream later

        # [long-term memory]
        longterm = self.m.longterm(learner_id)
        # [short-term memory]
        shortterm = self.m.shortterm(con_id=con_id)

        response = ""

        params = CompanionParams(
            # longterm
            user_memory=longterm,
            # shortterm
            history=shortterm,
            input=message,
        )

        # [build the final prompt]
        prompt = self.pb.companion_prompt(params)

        # [ask the brain to generate the companion's セリフ]

        async for token in self.b.think(prompt):
            response += token

        return response

    async def intervene(self, session_id):
        # TODO: to intervene, the companion
        # Currently after each interaction
        # Usually signals received from the learner
        # but prototype, we use simple signals from
        # session after interaction
        session = self.m.ses_repo.get_session_by_id(session_id)
        curr_goal_id = session["current_goal"]
        p = curr_goal_id not in session["retries"]

        retries = session["retries"]

        signals = {"pass": p, "retries": retries.get(curr_goal_id, 0)}

        if p:
            return "Good job"
        else:

            # Get the decision
            decision = self.b.make_decision(signals)

            activity = self.m.ac_repo.get_activity_by_id(session["activity_id"])
            goal = activity["goals"][curr_goal_id]

            # latest attempts
            content = session["history"][-1]["content"]

            # get the context from current activity and session

            # get the knowledge from the current goal
            knowledge = self.k.get_aps(activity["goals"][curr_goal_id]["atomic_points"])

            # prepare the prompt for the brain

            params = CompanionHelpParams(
                activity=activity["title"],
                goal=goal["goal"],
                latest_attempt=content,
                result="Correct" if p else "Incorrect",
                history=session["history"],
                knowledge=knowledge,
                type=decision,
            )

            # NOTE: Remember to build the prompt
            # from the params
            prompt = self.pb.companion_help_prompt(params)

            # print(rompt)

            response = ""

            async for token in self.b.think(prompt):
                response += token

            return response
