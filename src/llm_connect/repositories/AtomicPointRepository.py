# from llm_connect.proto.atomic_points import ATOMIC_REGISTRY

from llm_connect.proto.atomic_points_v2 import ATOMIC_REGISTRY


class AtomicPointRepository:
    def __init__(self):
        pass

    def get_atomic_point_by_id(self, ap_id: str):
        return ATOMIC_REGISTRY[ap_id]
