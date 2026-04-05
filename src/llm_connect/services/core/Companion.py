from openai import AsyncOpenAI

from llm_connect.configs.llm import GPT41
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.services.immerse.PromptBuilder import CompanionParams, PromptBuilder


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
        p = signals["pass"]

        if p:
            # TODO:
            # Learner has pass
            # Still suggest help
            # But good cultural immerse, ...
            # Improve learning skill
            pass
        else:
            # Learner failed
            # Based on retries
            retries = signals["retries"]

            if retries == 1:
                # nudge
                pass
            elif retries == 2:
                # scafford
                pass
            elif retries >= 3:
                # explaination
                pass


# NOTE: Memory and context together
class Memory:
    def __init__(
        self,
        learner_repo: LearnerRepository,
        con_repo: ConversationRepository,
    ):
        self.long_term = learner_repo
        self.short_term = con_repo

    def longterm(self, learner_id: str):
        profile = self.long_term.get_by_id(learner_id)
        return profile["proto"]

    def shortterm(self, con_id):
        con = self.short_term.get_conversation_by_id(con_id=con_id)
        messages = con["messages"]
        return messages


class Companion:
    def __init__(
        self,
        brain: Brain,
        memory: Memory,
        pb: PromptBuilder,
    ):
        self.b = brain
        self.m = memory
        self.pb = pb

    # TODO: Emulate the companion role
    # need learner_id, the current con_id, the current message
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

    async def intervene(self, session_id, signals):
        # TODO: to intervene, the companion
        pass
