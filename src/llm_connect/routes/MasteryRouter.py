from fastapi import APIRouter, Depends, Query

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_mastery_service
from llm_connect.schemas.pagination import PaginatedResponse
from llm_connect.services.MasteryService import MasteryService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/me/mastery", tags=["Mastery"])


@router.get("{id}")
async def get_mastery_detail(
    id: str,
    service: MasteryService = Depends(get_mastery_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = payload["sub"]
    return await service.get_mastery_detail(learner_id, id)


@router.get("")
async def get_all(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    # filters
    search: str | None = Query(None),
    mastery_level: str | None = Query(None),
    min_p: float | None = Query(None, ge=0, le=1),
    max_p: float | None = Query(None, ge=0, le=1),
    service: MasteryService = Depends(get_mastery_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = payload["sub"]
    res = await service.get_all_mastery(
        learner_id=learner_id,
        page=page,
        page_size=pageSize,
        search=search,
        mastery_level=mastery_level,
        min_p=min_p,
        max_p=max_p,
    )

    response = PaginatedResponse(
        items=res["items"],
        total=res["total"],
        page=res["page"],
        pageSize=res["page_size"],
    )

    return response


# @router.get(path="/")
# def get_all_mastery(
#     m_ser: MasteryService = Depends(get_mastery_service),
# ):
#     learner_id = "learner_001"

#     mastery = m_ser.get_all(learner_id)

#     return mastery
