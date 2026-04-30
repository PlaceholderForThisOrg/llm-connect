from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.repositories.TagRepository import TagRepository


class TagService:
    def __init__(self, session: AsyncSession, repo: TagRepository):
        self.session = session
        self.repo = repo

    async def create_tag(self, name: str):
        tag = await self.repo.create_tag(name)

        await self.session.commit()

        return tag

    async def get_paginated(self, page: int = 1, page_size: int = 10):
        offset = (page - 1) * page_size

        items = await self.repo.get_all(limit=page_size, offset=offset)
        total = await self.repo.count_all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    async def search_tags(self, query: str, page: int, page_size: int):
        offset = (page - 1) * page_size

        items = await self.repo.search(query, page_size, offset)
        total = await self.repo.count_search(query)

        return {"items": items, "total": total, "page": page, "page_size": page_size}
