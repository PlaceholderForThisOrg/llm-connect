from fastapi import Depends, Request
from openai import AsyncOpenAI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.services.ChatService import (
    ChatService,
    Evaluator,
    Orchestrator,
    PromptBuilder,
)
from llm_connect.services.LearnerService import LearnerService


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
def get_evaluator():
    return Evaluator()


def get_prompt_builder():
    return PromptBuilder()


def get_orchestrator(
    evaluator: Evaluator = Depends(get_evaluator),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
):
    return Orchestrator(evaluator, prompt_builder)


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
