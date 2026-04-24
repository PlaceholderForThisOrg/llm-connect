import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models.Tag import Tag


class TagRepository:
    def __init__(self, ses: AsyncSession):
        self.ses = ses
        self.db = ses
        self.session = ses

    async def create_tag(self, name: str) -> Tag:
        tag = Tag(
            id=str(uuid.uuid4()),
            name=name,
        )

        # stage the object
        self.ses.add(tag)
        # push to DB to get PK (if needed)
        await self.ses.flush()

        return tag

    async def get_all(self, limit: int = 10, offset: int = 0):
        stmt = select(Tag).order_by(Tag.name).limit(limit).offset(offset)

        result = await self.ses.execute(stmt)
        return result.scalars().all()

    async def count_all(self) -> int:
        stmt = select(func.count(Tag.id))
        result = await self.ses.execute(stmt)
        return result.scalar_one()

    async def search(self, query: str, limit: int = 10, offset: int = 0):
        stmt = (
            select(Tag)
            .where(func.lower(Tag.name).like(f"%{query.lower()}%"))
            .order_by(Tag.name)
            .limit(limit)
            .offset(offset)
        )

        result = await self.ses.execute(stmt)
        return result.scalars().all()

    async def count_search(self, query: str) -> int:
        stmt = select(func.count(Tag.id)).where(
            func.lower(Tag.name).like(f"%{query.lower()}%")
        )

        result = await self.ses.execute(stmt)
        return result.scalar_one()

    async def get_by_ids(self, ids: list[str]) -> list[Tag]:
        result = await self.db.execute(select(Tag).where(Tag.id.in_(ids)))
        return result.scalars().all()
