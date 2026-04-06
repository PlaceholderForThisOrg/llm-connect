from llm_connect.repositories.MasteryRepository import MasteryRepository


class MasteryService:
    def __init__(
        self,
        m_repo: MasteryRepository,
    ):
        self.m_repo = m_repo

    def get_all(self, learner_id: str):
        return self.m_repo.get_all(learner_id)
