from contextlib import asynccontextmanager

import asyncpg
import httpx
import redis
import redis.asyncio
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI

from llm_connect import logger
from llm_connect.configs.llm import ENDPOINT, TOKEN
from llm_connect.configs.postgre import POSTGRE_URI
from llm_connect.configs.redis import HOST, PORT


# 🪼 Define the app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        dsn=POSTGRE_URI(), min_size=1, max_size=5
    )

    app.state.llm = ChatCompletionsClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(TOKEN()),
    )

    app.state.redis = await redis.asyncio.Redis(host=HOST, port=PORT)

    app.state.http_client = httpx.AsyncClient()

    logger.logger.info("Application start")
    yield

    await app.state.pool.close()
    app.state.llm.close()
    await app.state.redis.close()
    await app.state.http_client.aclose()
    logger.logger.info("Clean client resources")
