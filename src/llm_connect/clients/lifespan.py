import json
from contextlib import asynccontextmanager

import aioboto3
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
from llm_connect.configs.s3 import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY_ID,
)


# 🪼 Define the app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    async def init_connection(conn):
        await conn.set_type_codec(
            "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
        )

    app.state.pool = await asyncpg.create_pool(
        dsn=POSTGRE_URI(), min_size=1, max_size=5, init=init_connection
    )

    app.state.llm = ChatCompletionsClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(TOKEN()),
    )

    app.state.redis = await redis.asyncio.Redis(host=HOST, port=PORT)

    app.state.http_client = httpx.AsyncClient()

    app.state.s3_session = aioboto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID(),
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ID(),
    )

    logger.logger.info("Application start")

    yield

    await app.state.pool.close()
    app.state.llm.close()
    await app.state.redis.aclose()
    await app.state.http_client.aclose()

    logger.logger.info("Clean client resources")
