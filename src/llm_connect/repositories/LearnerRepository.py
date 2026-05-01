# from sqlalchemy import select
import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from llm_connect.models.Learner import Learner

# from llm_connect.proto.learner_profile import profile


class LearnerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Learner | None:
        sql = (
            select(Learner)
            .where(Learner.user_id == user_id)
            .options(
                selectinload(Learner.conversations),
                selectinload(Learner.sessions),
                selectinload(Learner.mastery_records),
            )
        )

        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: str, **kwargs) -> "Learner":
        sql = (
            select(Learner)
            .where(Learner.user_id == user_id)
            .options(
                selectinload(Learner.conversations),
                selectinload(Learner.sessions),
                selectinload(Learner.mastery_records),
            )
        )

        result = await self.session.execute(sql)
        learner = result.scalar_one_or_none()

        if learner:
            return learner

        # Create new learner
        learner = Learner(
            user_id=user_id,
            name=kwargs.get("name", "New User"),
            nickname=kwargs.get("nickname", "newbie"),
            date_of_birth=kwargs.get("date_of_birth", datetime.date(2000, 1, 1)),
            avatar_url=kwargs.get("avatar_url"),
            settings=kwargs.get("settings", {}),
        )

        self.session.add(learner)
        await self.session.commit()
        await self.session.refresh(learner)

        return learner
