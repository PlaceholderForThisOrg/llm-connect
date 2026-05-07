from typing import List, Tuple

from sqlalchemy import bindparam, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models.AtomicPoint import AtomicPoint
from llm_connect.models.AtomicPointEmbedding import AtomicPointEmbedding


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in values) + "]"


class AtomicPointEmbeddingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(
        self,
        *,
        atomic_point_id,
        embedding_model: str,
        embedding_dims: int,
        semantic_text: str,
        content_hash: str | None,
        embedding: list[float],
    ) -> None:
        # Same asyncpg issue as search: ORM/core insert binds list as a string the
        # driver mishandles. Pass text literal + CAST(... AS vector).
        emb = _vector_literal(embedding)
        stmt = text(
            """
            INSERT INTO atomic_point_embedding (
                atomic_point_id,
                embedding_model,
                embedding_dims,
                semantic_text,
                content_hash,
                embedding,
                updated_at
            )
            VALUES (
                :aid,
                :model,
                :dims,
                :stext,
                :chash,
                CAST(:emb AS vector),
                NOW()
            )
            ON CONFLICT (atomic_point_id) DO UPDATE SET
                embedding = EXCLUDED.embedding,
                semantic_text = EXCLUDED.semantic_text,
                content_hash = EXCLUDED.content_hash,
                embedding_model = EXCLUDED.embedding_model,
                embedding_dims = EXCLUDED.embedding_dims,
                updated_at = NOW()
            """
        ).bindparams(
            bindparam("aid", atomic_point_id),
            bindparam("model", embedding_model),
            bindparam("dims", embedding_dims),
            bindparam("stext", semantic_text),
            bindparam("chash", content_hash),
            bindparam("emb", emb),
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def search_by_cosine(
        self,
        query_vector: list[float],
        limit: int,
    ) -> List[Tuple[AtomicPoint, str, float]]:
        # pgvector + asyncpg: passing a Python list into .cosine_distance() can be
        # compiled as a string bind that asyncpg mis-parses. Use PG text vector form.
        vec_str = _vector_literal(query_vector)
        distance_expr = text(
            "atomic_point_embedding.embedding <=> CAST(:qv AS vector)"
        ).bindparams(bindparam("qv", vec_str))

        stmt = (
            select(AtomicPoint, AtomicPointEmbedding.semantic_text, distance_expr)
            .join(
                AtomicPointEmbedding,
                AtomicPoint.id == AtomicPointEmbedding.atomic_point_id,
            )
            .order_by(distance_expr)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.all())
