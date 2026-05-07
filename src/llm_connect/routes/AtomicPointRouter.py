from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from llm_connect.clients.dependencies import (
    get_ap_embedding_service,
    get_ap_s,
)
from llm_connect.schemas.ap_schema import (
    CreateAPRequest,
    CreateAtomicPointRelationRequest,
    GetAtomicPointResponse,
    RAGSearchHit,
)
from llm_connect.schemas.pagination import PaginatedResponse
from llm_connect.services.AtomicPointEmbeddingService import (
    AtomicPointEmbeddingService,
)
from llm_connect.services.AtomicPointService import AtomicPointService

router = APIRouter(prefix="/api/v1/atomic-points", tags=["Atomic points"])


@router.get("/rag/search", response_model=List[RAGSearchHit])
async def rag_search_atomic_points(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=50),
    embedding_service: AtomicPointEmbeddingService = Depends(get_ap_embedding_service),
):
    return await embedding_service.search(query=q, limit=limit)


@router.post("/{ap_id}/rag/reindex")
async def rag_reindex_atomic_point(
    ap_id: UUID,
    service: AtomicPointService = Depends(get_ap_s),
):
    try:
        await service.reindex_atomic_point_for_rag(ap_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"reindexed": ap_id}


# @router.post("/")
# async def create_point(
#     # payload: Payload = Depends(verify_token),
# ):
#     return {"message": "OK"}


@router.delete("/{id}")
async def delete_atomic_point(
    id: UUID,
    force: bool = False,
    service: AtomicPointService = Depends(get_ap_s),
):
    await service.delete_atomic_point(id, force=force)
    return {
        "deleted": id,
    }


@router.post("/relations")
async def create_relation(
    request: CreateAtomicPointRelationRequest,
    service: AtomicPointService = Depends(get_ap_s),
):
    return await service.create_relation(request)


@router.get("/{id}")
async def get_point(
    id: str,
    ap_s: AtomicPointService = Depends(get_ap_s),
    service: AtomicPointService = Depends(get_ap_s),
):
    # return {"field": "value"}
    # return ap_s.get_ap(id)

    res = await service.get_atmomic_point(id)

    response = res
    return response


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
