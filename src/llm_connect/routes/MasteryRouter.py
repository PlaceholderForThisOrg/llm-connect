from fastapi import APIRouter, Depends

from llm_connect.clients.dependencies import get_mastery_service
from llm_connect.services.MasteryService import MasteryService

router = APIRouter(prefix="/api/v1/me/mastery", tags=["Mastery"])


@router.get(path="/")
def get_all_mastery(
    m_ser: MasteryService = Depends(get_mastery_service),
):
    learner_id = "learner_001"

    mastery = m_ser.get_all(learner_id)

    return mastery
