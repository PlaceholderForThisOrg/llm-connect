import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models.AtomicPoint import AtomicPoint
from llm_connect.models.AtomicPointTag import AtomicPointTag
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.AtomicPointTagRepository import AtomicPointTagRepository
from llm_connect.repositories.TagRepository import TagRepository
from llm_connect.schemas.ap_schema import CreateAPRequest


class AtomicPointService:
    def __init__(
        self,
        ap_repo: AtomicPointRepository,
        tag_repo: TagRepository,
        ap_tag_repo: AtomicPointTagRepository,
        session: AsyncSession,
    ):
        self.ap_repo = ap_repo
        self.tag_repo = tag_repo
        self.ap_tag_repo = ap_tag_repo
        self.session = session
        self.db = session
        self.repo = ap_repo

    def get_ap(self, id):
        return self.ap_repo.get_atomic_point_by_id(id)

    async def create_atomic_point(self, request: CreateAPRequest):
        # 1. validate tags exist
        # FIXME: Skip validation
        tags = await self.tag_repo.get_by_ids(request.tagIds)

        if len(tags) != len(request.tagIds):
            raise ValueError("Some tagIds are invalid")

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

        # finalize the transaction
        await self.db.commit()

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
