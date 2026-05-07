from enum import Enum
from typing import List, Optional
from uuid import UUID

from openai import AsyncOpenAI, BaseModel

from llm_connect import logger
from llm_connect.configs.llm import GPT4OMINI, GPT41
from llm_connect.models.Activity import BaseTask, TaskType
from llm_connect.proto.atomic_points import ap2str
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.InteractionRepository import InteractionRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.repositories.MasteryRepository import MasteryRepository
from llm_connect.repositories.MessageRepository import MessageRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.core.Bridge import Bridge
from llm_connect.services.immerse.PromptBuilder import (
    CompanionHelpParams,
    CompanionHelpParams_v1,
    CompanionHelpParams_v2,
    CompanionParams,
    CompanionSessionParams,
    IntentClassifierParams,
    PromptBuilder,
)


class Scope(str, Enum):
    GLOBAL = "global"
    SESSION_TASK = "session_task"


class Intent(str, Enum):
    CORRECTION = "correction"
    EXPLANATION = "explanation"
    ERROR_EXPLANATION = "error_explanation"
    TASK_HELP = "task_help"
    META = "meta"
    RECITE = "recite"
    RECOMMEND = "recommend"
    OTHER = "other"


class HelpLevel(str, Enum):
    NUDGE = "nudge"
    SCAFFORD = "scafford"
    EXPLANATION = "explanation"


class IntentionResult(BaseModel):
    intent: Intent
    scope: Scope
    confidence: float


class Persionality:
    def get_personality_1():
        return "You are very kind"

    def get_personality_2():
        return "You are a little angry"


class Knowledge:
    def __init__(
        self,
        ap_repo: AtomicPointRepository,
    ):
        self.ap_repo = ap_repo

    async def get_atomic_point(self, atomic_point_id: str):
        atomic_point = await self.ap_repo.get_by_id(atomic_point_id)

        return atomic_point

    def get_aps(self, ids: List[str]):
        aps = [ap2str(self.ap_repo.get_atomic_point_by_id(id)) for id in ids]

        return "\n".join(aps)


class Tool:
    def __init__(self, bridge: Bridge):
        self.bridge = bridge


class Brain:
    def __init__(
        self,
        llm: AsyncOpenAI,
        pb: PromptBuilder,
    ):
        self.llm = llm
        self.pb = pb

    async def detect_intent(
        self,
        message: str,
        has_active_task: bool,
        history: list[str] | None = None,
    ) -> IntentionResult:

        # [1] rule-based
        result = self._rule_based_intent(message, has_active_task)

        if result:
            return result

        # [2] llm fallback
        try:
            return await self._llm_classify(message, has_active_task, history)
        except Exception:
            # Safe fallback
            return IntentionResult(
                intent=Intent.OTHER,
                scope=Scope.SESSION_TASK if has_active_task else Scope.GLOBAL,
                confidence=0.3,
            )

    def _rule_based_intent(
        self,
        message: str,
        has_active_task: bool,
    ) -> Optional[IntentionResult]:
        msg = message.lower().strip()

        # correct
        if any(
            x in msg
            for x in ["is this correct", "check my", "correct this", "fix this"]
        ):
            return IntentionResult(
                intent=Intent.CORRECTION,
                scope=Scope.SESSION_TASK if has_active_task else Scope.GLOBAL,
                confidence=0.9,
            )

        # Detect sentence-like input (simple heuristic)
        # if re.match(r"^[a-zA-Z\s,'?.!]+$", msg) and len(msg.split()) > 3:
        #     # Likely user wrote a sentence → correction
        #     return IntentionResult(
        #         intent=Intent.CORRECTION,
        #         scope=Scope.SESSION_TASK if has_active_task else Scope.GLOBAL,
        #         confidence=0.6,
        #     )

        # error
        if any(
            x in msg
            for x in ["why is this wrong", "why wrong", "why error", "what's wrong"]
        ):
            return IntentionResult(
                intent=Intent.ERROR_EXPLANATION,
                scope=Scope.SESSION_TASK if has_active_task else Scope.GLOBAL,
                confidence=0.9,
            )

        # explain
        if any(x in msg for x in ["what is", "explain", "define", "what does mean"]):
            return IntentionResult(
                intent=Intent.EXPLANATION,
                scope=Scope.GLOBAL,
                confidence=0.85,
            )

        # task help
        if has_active_task and any(
            x in msg for x in ["help", "stuck", "don't know", "not sure", "how to do"]
        ):
            return IntentionResult(
                intent=Intent.TASK_HELP,
                scope=Scope.SESSION_TASK,
                confidence=0.85,
            )

        # recite
        if any(
            x in msg
            for x in ["quiz me", "test me", "flashcard", "recite", "practice words"]
        ):
            return IntentionResult(
                intent=Intent.RECITE,
                scope=Scope.GLOBAL,
                confidence=0.9,
            )

        # recommend
        if any(
            x in msg
            for x in ["recommend", "suggest", "what should i learn", "next lesson"]
        ):
            return IntentionResult(
                intent=Intent.RECOMMEND,
                scope=Scope.GLOBAL,
                confidence=0.85,
            )

        # meta
        if any(
            x in msg
            for x in ["what should i do", "what is this task", "how does this work"]
        ):
            return IntentionResult(
                intent=Intent.META,
                scope=Scope.SESSION_TASK if has_active_task else Scope.GLOBAL,
                confidence=0.8,
            )

        return None

    async def _llm_classify(
        self,
        message: str,
        has_active_task: bool,
        history: list[str] | None = None,
    ) -> IntentionResult:

        history_text = "\n".join(history[-3:]) if history else ""

        params = IntentClassifierParams(
            message=message, has_active_task=has_active_task, history=history_text
        )

        prompt = self.pb.intention_classify(params)

        response = await self.llm.chat.completions.create(
            model=GPT4OMINI,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()

        return IntentionResult.model_validate_json(content)

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
        mastery_repo: MasteryRepository,
        ap_repo: AtomicPointRepository,
        interaction_repo: InteractionRepository,
    ):
        self.long_term = learner_repo
        self.short_term = con_repo
        self.ses_repo = ses_repo
        self.ac_repo = ac_repo
        self.message_repo = message_repo
        self.mastery_repo = mastery_repo
        self.session_repo = ses_repo
        self.activity_repo = ac_repo
        self.ap_repo = ap_repo
        self.interaction_repo = interaction_repo

    async def get_latest_interaction(self, session_id, progress_id):
        interaction = await self.interaction_repo.get_latest_interaction(
            session_id, progress_id
        )

        if not interaction:
            return None

        return interaction

    async def get_current_session(self, session_id: str):
        session = await self.session_repo.get_full_session(session_id)

        if not session:
            raise KeyError("Session not found")

        return session

    async def get_current_progress(self, session_id: str):
        session = await self.session_repo.get_full_session(session_id)

        current_task_id = session.current_task

        current_progress = [p for p in session.progresses if p.id == current_task_id][0]

        return current_progress

    async def get_current_task(
        self,
        session_id: str,
        learner_id,
    ):
        session = await self.session_repo.get_session_detail(session_id, learner_id)
        activity_id = session.activity_id
        activity = await self.activity_repo.get_by_id(activity_id)

        current_task_id = session.current_task
        current_task = activity.tasks.get(current_task_id, None)

        if not current_task:
            raise KeyError("No task found")

        return current_task

    async def get_current_activity(self, activity_id: str):
        activity = await self.activity_repo.get_by_id(activity_id)

        return activity

    async def get_mastery(self, learner_id: str, atomic_point_id: str):
        mastery = await self.mastery_repo.get_mastery_by_id(learner_id, atomic_point_id)

        if not mastery:
            # no information
            return None

        return mastery

    async def get_history(self, conversation_id: str):
        messages = await self.message_repo.get_conversation_messages(conversation_id)

        return messages

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
        tool: Tool,
    ):
        self.b = brain
        self.m = memory
        self.k = k
        self.p = p
        self.pb = pb
        self.memory = self.m
        self.brain = self.b
        self.tool = tool

    def mode_explanation():
        None

    # use this to convert a task to the prompt
    def task_to_prompt(self, task: BaseTask) -> str:
        lines = []

        lines.append(f"Task ID: {task.id}")
        lines.append(f"Task Type: {task.type}")

        if task.prompt:
            lines.append(f"Prompt: {task.prompt}")

        if task.context:
            lines.append(f"Context: {task.context}")

        if task.hints:
            lines.append("Hints:")
            lines.extend(f"- {h}" for h in task.hints)

        # Type-specific fields
        match task.type:
            case TaskType.GENERATE:
                if task.sample_answers:
                    lines.append("Sample Answers:")
                    lines.extend(f"- {a}" for a in task.sample_answers)

                if task.keywords:
                    lines.append("Keywords:")
                    lines.extend(f"- {k}" for k in task.keywords)

            case TaskType.SELECT:
                if task.options:
                    lines.append("Options:")
                    lines.extend(f"{i}. {opt}" for i, opt in enumerate(task.options))

            case TaskType.FILL:
                if task.correct_answers:
                    lines.append("Accepted Answers:")
                    lines.extend(f"- {a}" for a in task.correct_answers)

                lines.append(f"Case Sensitive: {task.case_sensitive}")

            case TaskType.MATCH:
                if task.a:
                    lines.append("List A:")
                    lines.extend(f"{i}. {v}" for i, v in enumerate(task.a))

                if task.b:
                    lines.append("List B:")
                    lines.extend(f"{i}. {v}" for i, v in enumerate(task.b))

            case TaskType.REORDER:
                if task.options:
                    lines.append("Options:")
                    lines.extend(f"{i}. {v}" for i, v in enumerate(task.options))

        return "\n".join(lines)

    async def mode_task_help_v2(
        self,
        conversation_id: str,
        session_id: str,
        learner_id: str,
        message: str,
    ):
        # Load metadata
        personality = "You are a helpful English companion"
        session = await self.memory.get_current_session(session_id)
        activity = await self.memory.get_current_activity(session.activity_id)
        current_task = await self.memory.get_current_task(session_id, learner_id)
        # interaction = await self.memory.get_latest_interaction(session_id, current_task.id)

        logger.info("- Task to prompt")

        # Get related atomic points
        atomic_points = [
            await self.k.get_atomic_point(id) for id in current_task.atomic_points
        ]

        # Get messages
        messages = await self.m.shortterm_v2(conversation_id)

        params = CompanionHelpParams_v2(
            persionality=personality,
            type=activity.metadata.type,
            title=activity.metadata.title,
            description=current_task.prompt,
            npc=activity.metadata.npc,
            difficulty=activity.metadata.general_difficulty,
            content=activity.metadata.content,
            task=self.task_to_prompt(current_task),
            atomic_points=atomic_points,
            history=messages,
            # learner_input="",
            # help_level=HelpLevel.NUDGE,
            message=message,
        )

        prompt = self.pb.companion_help_prompt_v2(params)

        logger.info(prompt)

        async for token in self.b.think(prompt):
            yield token

    async def mode_task_help(
        self,
        conversation_id: str,
        session_id: str,
        learner_id: str,
        message: str,
    ):
        # TODO:
        intention = "Help the learner to complate the current task inside this activity"

        current_task = await self.memory.get_current_task(session_id, learner_id)

        atomic_points = [
            await self.k.get_atomic_point(id) for id in current_task.atomic_points
        ]

        messages = await self.m.shortterm_v2(conversation_id)

        params = CompanionHelpParams_v1(
            companion_personality="Not avalable",
            intention=intention,
            description=current_task.prompt,
            atomic_points=atomic_points,
            help_level=HelpLevel.NUDGE,
            history=messages,
            message=message,
        )

        prompt = self.pb.companion_help_prompt_v1(params)

        async for token in self.b.think(prompt):
            yield token

    def mode_meta():
        None

    def mode_recommend():
        None

    async def mode_other(
        self,
        learner_id: str,
        session_id: str,
        conversation_id: str,
        message: str,
    ):
        # intention = "Normal chat"
        messages = await self.memory.shortterm_v2(conversation_id)

        params = CompanionParams(
            # longterm
            user_memory="Currently not specified",
            # shortterm
            history=messages,
            input=message,
        )

        prompt = self.pb.companion_prompt(params)

        async for token in self.brain.think(prompt):
            yield token

    async def response_v3(
        self,
        learner_id: str,
        conversation_id: str,
        message: str,
        type: str,
        activity_id: str,
        session_id: str,
    ):
        # check whether or it is in the session
        has_active_task = True if type == "EMBEDDED" else False

        logger.info("[1] Get the intention of the current message")

        # rule-based and LLM-based
        intention = await self.b.detect_intent(
            message=message,
            has_active_task=has_active_task,
            # FIXME: skip history
            history="",
        )

        logger.info(f"Intention {intention.intent}")

        ##########
        if intention.intent == Intent.TASK_HELP:
            async for token in self.mode_task_help_v2(
                conversation_id,
                session_id,
                learner_id,
                message,
            ):
                yield token

        ##########
        else:
            async for token in self.mode_other(
                learner_id,
                session_id,
                conversation_id,
                message,
            ):
                yield token

    # FIXME: Delete
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
