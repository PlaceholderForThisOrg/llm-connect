from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models.Learner import Learner


class LearnerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str):
        result = await self.session.execute(
            select(Learner).where(Learner.user_id == user_id)
        )
        return result.scalar_one_or_none()
