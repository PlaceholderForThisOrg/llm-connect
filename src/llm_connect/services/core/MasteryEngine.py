from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect import logger
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.MasteryRepository import MasteryRepository
from llm_connect.services.core.BKTEngine import BKTEngine


class MasteryEngine:
    # NOTE: Use the BKTEngine first
    def __init__(
        self,
        engine: BKTEngine,
        m_repo: MasteryRepository,
        ap_repo: AtomicPointRepository,
        session: AsyncSession,
    ):
        self.e = engine
        self.m_repo = m_repo
        self.mastery_repo = m_repo
        self.atomic_point_repo = ap_repo
        self.session = session

    async def update_v2(self, result: bool, learner_id: str, ap_ids: List[str]):

        logger.info("Mastery engine start!")
        atomic_points = await self.atomic_point_repo.get_by_ids(ap_ids)
        ap_map = {str(ap.id): ap for ap in atomic_points}

        updated_masteries = []

        logger.debug(f"Atomic point's IDs: {ap_ids}")

        logger.debug(f"Atomic point's map: {ap_map}")

        for ap_id in ap_ids:
            # ap is None ?
            ap = ap_map.get(ap_id)

            logger.debug(f"Current atomic points: {ap.id}")

            if not ap:
                continue

            mastery = await self.mastery_repo.get_mastery_by_id(learner_id, ap_id)

            logger.debug(f"Mastery is None: {mastery is None}")

            is_new = False

            if not mastery:

                logger.debug("There is no mastery, create a new one")

                mastery = await self.mastery_repo.create_mastery(
                    learner_id=learner_id,
                    ap_id=ap_id,
                    p_L=ap.p_init,
                )
                is_new = True

            logger.debug(f"We have mastery: {mastery is not None}?")

            # update based on Bayesian Knowledge Tracing
            new_p_L = self.e.run(
                p_L=mastery.p_l,
                correct=result,
                p_guess=ap.p_guess,
                p_slip=ap.p_slip,
                p_learn=ap.p_learn,
            )

            mastery.p_l = new_p_L
            mastery.attempts += 1

            if result:
                mastery.correct_attempts += 1

            now = datetime.utcnow()
            if not mastery.first_attempt_at:
                mastery.first_attempt_at = now
            mastery.last_attempt_at = now

            if new_p_L > 0.9:
                mastery.mastery_level = "MASTER"
            elif new_p_L > 0.7:
                mastery.mastery_level = "ALMOST_MASTER"
            elif new_p_L > 0.3:
                mastery.mastery_level = "LEARNING"
            else:
                mastery.mastery_level = "BEGINNER"

            # only add this record if
            # this is new
            if is_new:
                await self.mastery_repo.create(mastery)

            updated_masteries.append(mastery)

        return updated_masteries

    def update(self, learner_id: str, ap_id: str, evidence):
        # Ensure the mastery has a record
        # self.m_repo.new_mastery(learner_id, ap_id)

        # Use the engine to have new mastery
        mastery = self.m_repo.get_mastery(learner_id, ap_id)
        params = {
            # L is the current estimated mastery
            # initialized from init
            "p_L": mastery["p_L"],
            "correct": evidence,
            "p_guess": mastery["p_guess"],
            "p_slip": mastery["p_slip"],
            "p_learn": mastery["p_learn"],
        }
        new_estimation = self.e.run(**params)

        self.m_repo.update_mastery(
            learner_id,
            ap_id,
            new_estimation,
        )

        return mastery
