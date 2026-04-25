import json
from contextlib import asynccontextmanager

import aioboto3
import asyncpg
import httpx
import redis
import redis.asyncio
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from llm_connect import logger
from llm_connect.configs.llm import ENDPOINT, TOKEN
from llm_connect.configs.mongodb import MONGODB_CONNECTION_STRING, MONGODB_DBNAME
from llm_connect.configs.postgre import POSTGRE_URI, POSTGRE_URL_v1
from llm_connect.configs.redis import HOST, PORT
from llm_connect.configs.s3 import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY_ID,
)
from llm_connect.models.Activity import Activity


# 🪼 Define the app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🗄️ database pools
    async def init_connection(conn):
        await conn.set_type_codec(
            "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
        )

    app.state.pool = await asyncpg.create_pool(
        dsn=POSTGRE_URI(), min_size=1, max_size=5, init=init_connection
    )

    # 🤓 LLM API
    app.state.llm = AsyncOpenAI(api_key=TOKEN(), base_url=ENDPOINT)

    # 💨 Redis client
    app.state.redis = await redis.asyncio.Redis(host=HOST, port=PORT)

    # 🛜 HTTP client
    app.state.http_client = httpx.AsyncClient()

    # 🌲 AWS async client
    app.state.s3_session = aioboto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID(),
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ID(),
    )

    # 😵‍💫 Engine for SQLAlchemy
    app.state.sqlalchemy_engine = create_async_engine(
        url=POSTGRE_URL_v1(),
        echo=True,
        future=True,
    )

    app.state.session_maker = sessionmaker(
        app.state.sqlalchemy_engine, class_=AsyncSession, expire_on_commit=False
    )

    # client used to connect Mongo
    app.state.mgdb_client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING())

    # init Beanie
    await init_beanie(
        database=app.state.mgdb_client[MONGODB_DBNAME()],
        document_models=[Activity],
    )

    logger.info("🚀 Application start 🚀")

    ####################################
    yield  # 😳
    ####################################

    await app.state.pool.close()
    await app.state.llm.close()
    await app.state.redis.aclose()
    await app.state.http_client.aclose()

    logger.info("🚥 Clean client resources 🚥")
