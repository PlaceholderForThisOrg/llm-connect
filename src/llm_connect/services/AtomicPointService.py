import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect import logger
from llm_connect.models import AtomicPointRelation
from llm_connect.models.AtomicPoint import AtomicPoint
from llm_connect.models.AtomicPointTag import AtomicPointTag
from llm_connect.repositories.AtomicPointRelationRepository import (
    AtomicPointRelationRepository,
)
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.AtomicPointTagRepository import AtomicPointTagRepository
from llm_connect.repositories.TagRepository import TagRepository
from llm_connect.schemas.ap_schema import (
    CreateAPRequest,
    CreateAtomicPointRelationRequest,
)
from llm_connect.services.AtomicPointEmbeddingService import (
    AtomicPointEmbeddingService,
)


class AtomicPointService:
    def __init__(
        self,
        ap_repo: AtomicPointRepository,
        tag_repo: TagRepository,
        ap_tag_repo: AtomicPointTagRepository,
        session: AsyncSession,
        ap_relation_repo: AtomicPointRelationRepository,
        embedding_service: AtomicPointEmbeddingService,
    ):
        self.ap_repo = ap_repo
        self.tag_repo = tag_repo
        self.ap_tag_repo = ap_tag_repo
        self.session = session
        self.db = session
        self.repo = ap_repo
        self.ap_relation_repo = ap_relation_repo
        self.embedding_service = embedding_service

    async def delete_atomic_point(self, ap_id: uuid.UUID, force: bool = False):
        atomic_point = await self.repo.get_by_id_with_relations(ap_id)

        if not atomic_point:
            raise ValueError("Atomic point not found")

        if not force:
            if atomic_point.incoming_relations:
                raise ValueError(
                    "Cannot delete: other atomic points depend on this one"
                )

            if atomic_point.mastery_records:
                raise ValueError("Cannot delete: mastery records exist")

        # Remove atomic points, all mastery, all relation
        await self.repo.delete(atomic_point)

        return ap_id

    async def create_relation(self, request: CreateAtomicPointRelationRequest):

        # node validation
        from_ap = await self.ap_repo.get_by_id(request.from_id)
        to_ap = await self.ap_repo.get_by_id(request.to_id)

        if not from_ap or not to_ap:
            raise ValueError("AtomicPoint not found")

        # prevent self loop
        if request.from_id == request.to_id:
            raise ValueError("Cannot create self-relation")

        # duplicate relation
        existing = await self.ap_relation_repo.find_relation(
            request.from_id, request.to_id, request.relation_type
        )

        if existing:
            raise ValueError("Relation already exists")

        # relation creation
        relation = AtomicPointRelation(
            from_id=request.from_id,
            to_id=request.to_id,
            relation_type=request.relation_type,
            weight=request.weight,
        )

        await self.ap_relation_repo.create(relation)

        # commit the session
        await self.session.commit()

        return relation

    async def get_atmomic_point(self, id: str):
        model = await self.repo.get_by_id(id)

        if model is None:
            raise KeyError(f"No atomic point with id: {id}")

        return model

    def get_ap(self, id):
        return self.ap_repo.get_atomic_point_by_id(id)

    async def create_atomic_point(self, request: CreateAPRequest):
        # 1. validate tags exist
        # FIXME: Skip validation
        # tags = await self.tag_repo.get_by_names(request.tags)
        tags = await self.tag_repo.get_or_create_by_names(request.tags)

        if len(tags) != len(request.tags):
            raise ValueError("Some tag's names are invalid")

        atomic_point = AtomicPoint(
            id=str(uuid.uuid4()),
            type=request.type,
            name=request.name,
            description=request.description,
            examples=request.examples,
            level=request.level,
            popularity=request.popularity,
        )

        await self.ap_repo.create(atomic_point)

        # relation
        relations = [
            AtomicPointTag(ap_id=atomic_point.id, tag_id=tag.id) for tag in tags
        ]

        await self.ap_tag_repo.bulk_create(relations)

        # relationship between atomic points
        if request.relations:
            graph_relations = [
                AtomicPointRelation(
                    from_id=atomic_point.id,
                    to_id=rel.to_id,
                    relation_type=rel.relation_type,
                    weight=rel.weight,
                )
                for rel in request.relations
            ]

            await self.ap_relation_repo.bulk_create(graph_relations)

        # finalize the transaction
        await self.db.commit()

        try:
            await self.embedding_service.index_atomic_point(atomic_point)
        except Exception:
            logger.exception(
                "RAG embedding index failed for atomic_point id=%s",
                atomic_point.id,
            )

        return atomic_point

    async def search_atomic_points(
        self,
        search: Optional[str],
        type: Optional[str],
        level: Optional[str],
        tags: Optional[List[str]],
        min_popularity: Optional[float],
        page: int,
        page_size: int,
    ):
        items, total = await self.repo.search(
            search=search,
            type=type,
            level=level,
            tags=tags,
            min_popularity=min_popularity,
            page=page,
            page_size=page_size,
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def reindex_atomic_point_for_rag(self, ap_id: uuid.UUID):
        atomic_point = await self.repo.get_by_id(str(ap_id))
        if atomic_point is None:
            raise ValueError("Atomic point not found")
        await self.embedding_service.index_atomic_point(atomic_point)
