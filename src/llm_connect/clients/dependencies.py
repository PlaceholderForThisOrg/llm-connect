from fastapi import Depends, Request
from openai import AsyncOpenAI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.services.ActivityService import ActivityService
from llm_connect.services.analyzer import Analyzer
from llm_connect.services.ChatService import ChatService
from llm_connect.services.core.aevaluator import AEvaluator
from llm_connect.services.core.RolePlaySessionManager import RolePlaySessionManager
from llm_connect.services.immerse import Actor, Evaluator, Orchestrator, PromptBuilder
from llm_connect.services.LearnerService import LearnerService
from llm_connect.services.SessionService import SessionService


# 🤷‍♂️ Outside clients, created in lifespan
def get_llm(request: Request):
    return request.app.state.llm


def get_postgre_pool(request: Request):
    return request.app.state.pool


def get_redis(request: Request):
    return request.app.state.redis


def get_http_client(request: Request):
    return request.app.state.http_client


def get_s3_session(request: Request):
    return request.app.state.s3_session


async def get_db_session(request: Request):
    async with request.app.state.session_maker() as session:
        yield session


# 😵‍💫 Controlled services/repositories
# router is linked to app already
def get_prompt_builder():
    return PromptBuilder()


def get_evaluator(
    client: AsyncOpenAI = Depends(get_llm),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
):
    return Evaluator(client, prompt_builder)


def get_actor(
    client: AsyncOpenAI = Depends(get_llm),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
):
    return Actor(client, prompt_builder)


def get_analyzer():
    return Analyzer()


def get_aevaluator():
    return AEvaluator()


def get_session_repo():
    return SessionRepository()


def get_roleplay_session_manager(
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    client: AsyncOpenAI = Depends(get_llm),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    return RolePlaySessionManager(
        prompt_builder,
        client,
        session_repo,
    )


def get_activity_repo():
    return ActivityRepository()


def get_orchestrator(
    evaluator: Evaluator = Depends(get_evaluator),
    actor: Actor = Depends(get_actor),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    analyzer: Analyzer = Depends(get_analyzer),
    aevaluator: AEvaluator = Depends(get_aevaluator),
    session_manager: RolePlaySessionManager = Depends(get_roleplay_session_manager),
    session_repo: SessionRepository = Depends(get_session_repo),
    activity_repo: ActivityRepository = Depends(get_activity_repo),
):
    return Orchestrator(
        evaluator,
        actor,
        prompt_builder,
        analyzer,
        aevaluator,
        session_manager,
        session_repo,
        activity_repo,
    )


def get_chat_service(
    llm: AsyncOpenAI = Depends(get_llm),
    redis: Redis = Depends(get_redis),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    return ChatService(llm, redis, orchestrator)


def get_learner_repository(session: AsyncSession = Depends(get_db_session)):
    return LearnerRepository(session)


def get_learner_service(
    learner_repository: LearnerRepository = Depends(get_learner_repository),
):
    return LearnerService(learner_repository)


def get_session_service(
    orchestrator: Orchestrator = Depends(get_orchestrator),
    session_repo: SessionRepository = Depends(get_session_repo),
    activity_repo: ActivityRepository = Depends(get_activity_repo),
):
    return SessionService(
        orchestrator,
        session_repo,
        activity_repo,
    )


def get_activity_service(
    activity_repo: ActivityRepository = Depends(get_activity_repo),
):
    return ActivityService(activity_repo)
