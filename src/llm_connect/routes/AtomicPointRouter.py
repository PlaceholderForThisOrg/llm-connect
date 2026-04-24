from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from llm_connect.clients.dependencies import get_ap_s
from llm_connect.schemas.ap_schema import CreateAPRequest, GetAtomicPointResponse
from llm_connect.schemas.pagination import PaginatedResponse
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

    # FIXME: hide important model's field
    return ap


@router.get("/", response_model=PaginatedResponse[GetAtomicPointResponse])
async def search_atomic_points(
    search: Optional[str] = None,
    type: Optional[str] = None,
    level: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
    min_popularity: Optional[float] = None,
    page: int = 1,
    page_size: int = 20,
    service: AtomicPointService = Depends(get_ap_s),
):
    res = await service.search_atomic_points(
        search=search,
        type=type,
        level=level,
        tags=tags,
        min_popularity=min_popularity,
        page=page,
        page_size=page_size,
    )

    response = PaginatedResponse(
        items=[GetAtomicPointResponse.from_model(ap) for ap in res["items"]],
        total=res["total"],
        page=res["page"],
        pageSize=res["page_size"],
    )

    return response
