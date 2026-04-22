from sqlalchemy.ext.asyncio import AsyncSession


class TagRepository:
    def __init__(self, ses: AsyncSession):
        self.ses = ses

    async def create_tag(self, name : str):
        