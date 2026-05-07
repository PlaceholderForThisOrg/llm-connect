"""
Seed atomic_point rows (and RAG embeddings when the embedding API is available).

Usage (from repo root):

  uv run python scripts/seed_atomic_points.py

Requires .env / .env.development with DB and LLM settings (same as the app).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

load_dotenv(_REPO_ROOT / ".env.development", verbose=True)
load_dotenv(_REPO_ROOT / ".env", verbose=True)

from llm_connect import logger  # noqa: E402
from llm_connect.configs.llm import ENDPOINT, TOKEN  # noqa: E402
from llm_connect.configs.postgre import POSTGRE_URL_v1  # noqa: E402
from llm_connect.repositories.AtomicPointEmbeddingRepository import (  # noqa: E402
    AtomicPointEmbeddingRepository,
)
from llm_connect.repositories.AtomicPointRelationRepository import (  # noqa: E402
    AtomicPointRelationRepository,
)
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository  # noqa: E402
from llm_connect.repositories.AtomicPointTagRepository import (  # noqa: E402
    AtomicPointTagRepository,
)
from llm_connect.repositories.TagRepository import TagRepository  # noqa: E402
from llm_connect.schemas.ap_schema import CreateAPRequest  # noqa: E402
from llm_connect.services.AtomicPointEmbeddingService import (  # noqa: E402
    AtomicPointEmbeddingService,
)
from llm_connect.services.AtomicPointService import AtomicPointService  # noqa: E402
from pgvector.asyncpg import register_vector  # noqa: E402


def _examples_from_proto(value: str | list) -> str:
    if isinstance(value, str):
        return value
    return "\n".join(f"- {x}" for x in value)


SEED_ATOMIC_POINTS: list[dict] = [
    {
        "type": "grammar",
        "name": "Polite requests with 'could' and 'would'",
        "description": "Used to make polite requests in service situations.",
        "examples": _examples_from_proto(
            ["Could I see the menu?", "Would you bring us some water?"]
        ),
        "level": "B1",
        "popularity": 0.95,
        "tags": ["restaurant", "politeness"],
    },
    {
        "type": "grammar",
        "name": "Using 'some' and 'any' for requests",
        "description": "Used to talk about quantities in questions and requests.",
        "examples": _examples_from_proto(
            ["Can I have some water?", "Do you have any vegetarian dishes?"]
        ),
        "level": "B1",
        "popularity": 0.9,
        "tags": ["food", "quantity"],
    },
    {
        "type": "vocabulary",
        "name": "Tableware and place-setting words",
        "description": "Nouns for items commonly used when eating out.",
        "examples": _examples_from_proto(
            ["fork", "knife", "spoon", "napkin", "plate", "glass"]
        ),
        "level": "A2",
        "popularity": 0.88,
        "tags": ["restaurant", "nouns"],
    },
    {
        "type": "fluency",
        "name": "Ordering food politely",
        "description": "Fixed chunks for placing an order in a restaurant.",
        "examples": _examples_from_proto(
            [
                "I'd like the pasta, please.",
                "Could we get two coffees?",
                "We'll have the bill, please.",
            ]
        ),
        "level": "B1",
        "popularity": 0.92,
        "tags": ["restaurant", "chunks"],
    },
    {
        "type": "grammar",
        "name": "Present simple for habits and routines",
        "description": (
            "Use the present simple for repeated actions, habits, and general truths."
        ),
        "examples": _examples_from_proto(
            [
                "I start work at nine every day.",
                "Water boils at 100°C.",
            ]
        ),
        "level": "A2",
        "popularity": 0.87,
        "tags": ["tense", "daily-life"],
    },
]


async def main() -> None:
    engine = create_async_engine(POSTGRE_URL_v1(), echo=False, future=True)

    @event.listens_for(engine.sync_engine, "connect")
    def _register_pgvector(dbapi_connection, connection_record):
        dbapi_connection.run_async(register_vector)

    session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    llm = AsyncOpenAI(api_key=TOKEN(), base_url=ENDPOINT)
    created_ids: list[str] = []

    async with session_factory() as session:
        ap_repo = AtomicPointRepository(session)
        tag_repo = TagRepository(ses=session)
        ap_tag_repo = AtomicPointTagRepository(session=session)
        ap_relation_repo = AtomicPointRelationRepository(session)
        emb_repo = AtomicPointEmbeddingRepository(session)
        emb_svc = AtomicPointEmbeddingService(llm=llm, repo=emb_repo)
        svc = AtomicPointService(
            ap_repo=ap_repo,
            tag_repo=tag_repo,
            ap_tag_repo=ap_tag_repo,
            session=session,
            ap_relation_repo=ap_relation_repo,
            embedding_service=emb_svc,
        )

        for row in SEED_ATOMIC_POINTS:
            data = dict(row)
            tags = data.pop("tags", []) or []
            req = CreateAPRequest(
                type=data["type"],
                name=data["name"],
                description=data["description"],
                examples=data["examples"],
                level=data["level"],
                popularity=data["popularity"],
                tags=tags,
                relations=None,
            )
            ap = await svc.create_atomic_point(req)
            created_ids.append(str(ap.id))
            logger.info("Seeded atomic_point id=%s name=%r", ap.id, ap.name)

    await engine.dispose()
    await llm.close()
    print(json.dumps({"seeded_count": len(created_ids), "ids": created_ids}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
