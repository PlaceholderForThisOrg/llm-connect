# from llm_connect.proto.atomic_points import ATOMIC_REGISTRY

from llm_connect.models.AtomicPoint import AtomicPoint
from llm_connect.proto.atomic_points_v2 import ATOMIC_REGISTRY
from sqlalchemy.ext.asyncio import AsyncSession


class AtomicPointRepository:
    def __init__(self, session : AsyncSession):
        self.session = session

    def get_atomic_point_by_id(self, ap_id: str):
        return ATOMIC_REGISTRY[ap_id]
    
    async def create(self, atomic_point: AtomicPoint):
        self.session.add(atomic_point)
        await self.session.flush()
        return atomic_point
