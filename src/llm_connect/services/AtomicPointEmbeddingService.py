import hashlib

from openai import AsyncOpenAI

from llm_connect.configs.embedding import embedding_dimensions, embedding_model
from llm_connect.models.AtomicPoint import AtomicPoint
from llm_connect.repositories.AtomicPointEmbeddingRepository import (
    AtomicPointEmbeddingRepository,
)
from llm_connect.schemas.ap_schema import RAGSearchHit
from llm_connect.services.atomic_point_semantic import build_semantic_text


class AtomicPointEmbeddingService:
    def __init__(
        self,
        llm: AsyncOpenAI,
        repo: AtomicPointEmbeddingRepository,
    ):
        self.llm = llm
        self.repo = repo

    async def embed_text(self, text: str) -> list[float]:
        model = embedding_model()
        dims = embedding_dimensions()
        input_text = text.replace("\n", " ")
        response = await self.llm.embeddings.create(
            model=model,
            input=input_text,
            dimensions=dims,
        )
        return list(response.data[0].embedding)

    async def index_atomic_point(self, ap: AtomicPoint) -> None:
        semantic = build_semantic_text(ap)
        digest = hashlib.sha256(semantic.encode("utf-8")).hexdigest()
        vec = await self.embed_text(semantic)
        await self.repo.upsert(
            atomic_point_id=ap.id,
            embedding_model=embedding_model(),
            embedding_dims=embedding_dimensions(),
            semantic_text=semantic,
            content_hash=digest,
            embedding=vec,
        )

    async def search(self, query: str, limit: int = 5) -> list[RAGSearchHit]:
        qv = await self.embed_text(query)
        rows = await self.repo.search_by_cosine(qv, limit)
        return [
            RAGSearchHit(
                atomic_point_id=ap.id,
                name=ap.name,
                type=ap.type,
                level=ap.level,
                cosine_distance=float(dist),
                semantic_text=sem_text,
            )
            for ap, sem_text, dist in rows
        ]
