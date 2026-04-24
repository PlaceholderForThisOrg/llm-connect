from fastapi import APIRouter, Depends

from llm_connect.clients.dependencies import get_ap_s
from llm_connect.schemas.ap_schema import CreateAPRequest
from llm_connect.services.AtomicPointService import AtomicPointService

router = APIRouter(prefix="/api/v1/atomic-points", tags=["Atomic points"])


# @router.post("/")
# async def create_point(
#     # payload: Payload = Depends(verify_token),
# ):
#     return {"message": "OK"}


@router.get("/{id}")
def get_point(
    id: str,
    ap_s: AtomicPointService = Depends(get_ap_s),
):
    # return {"field": "value"}
    return ap_s.get_ap(id)


@router.post("/")
async def create_atomic_point(
    request: CreateAPRequest,
    service: AtomicPointService = Depends(get_ap_s),
):
    ap = await service.create_atomic_point(request)

    # FIXME: filter import field
    return ap
