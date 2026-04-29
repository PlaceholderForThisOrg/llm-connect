from llm_connect.repositories.MasteryRepository import MasteryRepository


class MasteryService:
    def __init__(
        self,
        m_repo: MasteryRepository,
    ):
        self.m_repo = m_repo
        self.repo = m_repo
        self.mastery_repo = m_repo

    async def get_mastery_detail(self, learner_id: str, atomic_point_id: str) -> dict:
        mastery = await self.mastery_repo.get_mastery(learner_id, atomic_point_id)

        if not mastery:
            raise ValueError("Mastery not found")

        accuracy = (
            mastery.correct_attempts / mastery.attempts if mastery.attempts > 0 else 0
        )

        days_active = None
        if mastery.first_attempt_at and mastery.last_attempt_at:
            days_active = (mastery.last_attempt_at - mastery.first_attempt_at).days

        # Simple heuristic insights
        improving = mastery.p_l >= 0.6 and accuracy >= 0.6
        needs_review = mastery.p_l < 0.4 and mastery.attempts > 5

        return {
            "learner_id": learner_id,
            "atomic_point_id": atomic_point_id,
            "mastery": {
                "p_l": mastery.p_l,
                "mastery_level": mastery.mastery_level,
                "attempts": mastery.attempts,
                "correct_attempts": mastery.correct_attempts,
                "accuracy": round(accuracy, 2),
            },
            "time": {
                "first_attempt_at": mastery.first_attempt_at,
                "last_attempt_at": mastery.last_attempt_at,
                "days_active": days_active,
            },
            "insights": {
                "improving": improving,
                "needs_review": needs_review,
            },
        }

    async def get_all_mastery(
        self,
        learner_id: str,
        page: int = 1,
        page_size: int = 20,
        **filters,
    ):
        # validation
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)  # cap to avoid abuse

        offset = (page - 1) * page_size

        items = await self.repo.get_mastery_overview(
            learner_id=learner_id, offset=offset, limit=page_size, **filters
        )

        total = await self.repo.count_mastery(learner_id=learner_id, **filters)

        return {
            "items": [
                {
                    "atomic_point_id": m.atomic_point_id,
                    "atomic_point_name": m.atomic_point.name,
                    "p_l": m.p_l,
                    "mastery_level": m.mastery_level,
                }
                for m in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_all(self, learner_id: str):
        return self.m_repo.get_all(learner_id)
