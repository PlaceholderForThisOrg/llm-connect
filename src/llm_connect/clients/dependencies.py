from fastapi import Depends, Request
from openai import AsyncOpenAI
from redis.asyncio import Redis

from llm_connect.services.chat_service import (
    ChatService,
    Evaluator,
    Orchestrator,
    PromptBuilder,
)


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
