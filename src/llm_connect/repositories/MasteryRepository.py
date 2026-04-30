import json
import os
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from llm_connect.models import AtomicPoint
from llm_connect.models.Mastery import Mastery
from llm_connect.proto.masteries_v1 import masteries_v1


class MasteryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.db = session

        self.file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../proto/runtime_db/masteries.json"
            )
        )

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    masteries_v1.update(data)
            except Exception:
                pass

        # Initial sync to ensure file exists
        self.sync()

    async def create(self, mastery):
        self.session.add(mastery)

    # async def create_mastery(self, learner_id: str, ap_id: str, p_l: float):
    #     mastery = Mastery(
    #         learner_id=learner_id,
    #         atomic_point_id=ap_id,
    #         p_l=p_l,
    #         attempts=0,
    #         correct_attempts=0,
    #         mastery_level="not_started",
    #     )
    #     self.session.add(mastery)
    #     return mastery

    async def get_mastery(
        self, learner_id: str, atomic_point_id: str
    ) -> Optional[Mastery]:
        stmt = (
            select(Mastery)
            .where(Mastery.learner_id == learner_id)
            .where(Mastery.atomic_point_id == atomic_point_id)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_mastery(
        self,
        learner_id: str,
        search: str | None = None,
        mastery_level: str | None = None,
        min_p: float | None = None,
        max_p: float | None = None,
    ):
        query = (
            select(func.count())
            .select_from(Mastery)
            .where(Mastery.learner_id == learner_id)
        )

        if mastery_level:
            query = query.where(Mastery.mastery_level == mastery_level)

        if min_p is not None:
            query = query.where(Mastery.p_l >= min_p)

        if max_p is not None:
            query = query.where(Mastery.p_l <= max_p)

        if search:
            query = query.join(Mastery.atomic_point).where(
                func.lower(AtomicPoint.name).like(f"%{search.lower()}%")
            )

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_mastery_overview(
        self,
        learner_id: str,
        search: str | None = None,
        mastery_level: str | None = None,
        min_p: float | None = None,
        max_p: float | None = None,
        limit: int = 20,
        offset: int = 0,
    ):
        query = (
            select(Mastery)
            .where(Mastery.learner_id == learner_id)
            .options(selectinload(Mastery.atomic_point))
        )

        # filtering
        filters = []

        if mastery_level:
            filters.append(Mastery.mastery_level == mastery_level)

        if min_p is not None:
            filters.append(Mastery.p_l >= min_p)

        if max_p is not None:
            filters.append(Mastery.p_l <= max_p)

        if filters:
            query = query.where(and_(*filters))

        if search:
            query = query.join(Mastery.atomic_point).where(
                func.lower(AtomicPoint.name).like(f"%{search.lower()}%")
            )

        # sorting
        query = query.order_by(Mastery.p_l.asc())

        # pagination
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        items = result.scalars().all()

        return items

    async def get_mastery_by_id(
        self,
        learner_id: str,
        ap_id: str,
    ) -> Optional[Mastery]:
        stmt = select(Mastery).where(
            Mastery.learner_id == learner_id,
            Mastery.atomic_point_id == ap_id,
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_mastery(
        self,
        learner_id: str,
        ap_id: str,
        p_L: float,
    ) -> Mastery:
        mastery = Mastery(
            learner_id=learner_id,
            atomic_point_id=ap_id,
            p_l=p_L,
            attempts=0,
            correct_attempts=0,
            first_attempt_at=None,
            last_attempt_at=None,
            mastery_level="not_started",
        )

        self.session.add(mastery)

        # flush not commit
        await self.session.flush()

        return mastery

    def sync(self):
        """Write current mastery to file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(masteries_v1, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[sync error] {e}")

    def new_mastery(self, learner_id: str, ap_id: str):
        if ap_id in masteries_v1[learner_id]:
            return None

        else:
            # not in, initialize
            # FIXME: Just an estimation
            # of the mastery of the current
            # atomic point
            mastery = {
                # parameters
                "p_init": 0.3,
                "p_learn": 0.15,
                "p_guess": 0.3,
                "p_slip": 0.2,
                # initial mastery estimation
                "p_L": 0.3,
            }

            masteries_v1[learner_id][ap_id] = mastery
            self.sync()

    # def get_mastery(
    #     self,
    #     learner_id: str,
    #     ap_id: str,
    # ):
    #     if ap_id not in masteries_v1[learner_id]:
    #         self.new_mastery(learner_id, ap_id)
    #     return masteries_v1[learner_id][ap_id]

    def update_mastery(
        self,
        learner_id: str,
        ap_id: str,
        new_estimation: float,
    ):
        mastery = self.get_mastery(learner_id, ap_id)
        mastery["p_L"] = new_estimation

        self.sync()

        return mastery

    def get_all(
        self,
        learner_id: str,
    ):
        # object of mastery record
        mastery = masteries_v1[learner_id]
        return mastery
