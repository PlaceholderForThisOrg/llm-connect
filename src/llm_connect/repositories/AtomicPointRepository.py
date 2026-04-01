from llm_connect.proto.atomic_points import ATOMIC_REGISTRY


class AtomicPointRepository:
    def __init__(self):
        pass

    def get_atomic_point_by_id(self, ap_id: str):
        return ATOMIC_REGISTRY[ap_id]
