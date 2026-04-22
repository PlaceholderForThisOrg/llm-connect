# from sqlalchemy import select
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models.Learner import Learner

# from llm_connect.proto.learner_profile import profile


class LearnerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Learner | None:
        # Build the SQL
        sql = select(Learner).where(Learner.user_id == user_id)
        # Execute
        result = await self.session.execute(sql)

        return result.scalar_one_or_none()
