from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_tag_ser
from llm_connect.schemas.tag_schema import (
    CreateTagRequest,
    CreateTagResponse,
    GetAllTagResponse,
)
from llm_connect.services.TagService import TagService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])


@router.post(
    "/",
    response_model=CreateTagResponse,
)
async def create_tag(
    request: CreateTagRequest,
    service: TagService = Depends(get_tag_ser),
    payload: Payload = Depends(verify_token),
):
    created = await service.create_tag(request.name)

    response = CreateTagResponse(id=created.id, name=created.name)

    return response


# @router.get("/", response_model=GetAllTagResponse,)
# async def get_all_tags(
#     page : int,
#     pageSize : int,
#     service : TagService = Depends(get_tag_ser),
#     payload: Payload = Depends(verify_token),
# ):
#     res = await service.get_paginated(page, page_size=pageSize)

#     response = GetAllTagResponse(
#         items=res["items"],
#         total=res["total"],
#         page=res["page"],
#         pageSize=res["page_size"]
#     )

#     return response

# @router.get("/", response_model=GetAllTagResponse,)
# async def get_all_tags(
#     query : str,
#     page : int,
#     pageSize : int,
#     service : TagService = Depends(get_tag_ser),
#     payload: Payload = Depends(verify_token),
# ):
#     res = await service.search_tags(query=query, page=page, page_size=pageSize)

#     response = GetAllTagResponse(
#         items=res["items"],
#         total=res["total"],
#         page=res["page"],
#         pageSize=res["page_size"]
#     )

#     return response


@router.get("/", response_model=GetAllTagResponse)
async def get_tags(
    query: str | None = None,
    page: int = 1,
    pageSize: int = 10,
    service: TagService = Depends(get_tag_ser),
    payload: Payload = Depends(verify_token),
):
    if query:
        res = await service.search_tags(query=query, page=page, page_size=pageSize)
    else:
        res = await service.get_paginated(page=page, page_size=pageSize)

    return GetAllTagResponse(
        items=res["items"],
        total=res["total"],
        page=res["page"],
        pageSize=res["page_size"],
    )
