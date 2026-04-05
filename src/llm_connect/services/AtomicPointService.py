from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository


class AtomicPointService:
    def __init__(
        self,
        ap_repo: AtomicPointRepository,
    ):
        self.ap_repo = ap_repo

    def get_ap(self, id):
        return self.ap_repo.get_atomic_point_by_id(id)
