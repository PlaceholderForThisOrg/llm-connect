from llm_connect.repositories.MasteryRepository import MasteryRepository
from llm_connect.services.core.BKTEngine import BKTEngine


class MasteryEngine:
    # NOTE: Use the BKTEngine first
    def __init__(
        self,
        engine: BKTEngine,
        m_repo: MasteryRepository,
    ):
        self.e = engine
        self.m_repo = m_repo

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
