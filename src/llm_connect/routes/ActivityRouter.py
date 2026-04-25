from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_activity_service
from llm_connect.schemas.activity_schema import (
    CreateActivityRequest,
    GetActivityResponse,
)
from llm_connect.schemas.pagination import PaginatedResponse
from llm_connect.services.ActivityService import ActivityService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/activities", tags=["Tasks", "Activities"])


@router.get("/{activity_id}")
async def get_activity(
    activity_id: str,
    activity_service: ActivityService = Depends(get_activity_service),
):
    activity = activity_service.get_activity(activity_id)

    response = GetActivityResponse(
        activityId=activity_id,
        type=activity["type"],
        title=activity["title"],
        metadata=activity["metadata"],
        goals=activity["goals"],
    )

    return response


# @router.get("/")
# def get_activities(
#     a_s: ActivityService = Depends(get_activity_service),
# ):
#     activities = a_s.get_activities()


#     return activities
@router.get("/")
async def get_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=50),
    title: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    difficulty: Optional[str] = None,
    type_: Optional[str] = Query(None, alias="type"),
    # payload: Payload = Depends(verify_token),
    service: ActivityService = Depends(get_activity_service),
):
    result = await service.get_activities_v2(
        page=page,
        page_size=page_size,
        title=title,
        tags=tags,
        difficulty=difficulty,
        type_=type_,
    )

    return result


@router.post("/")
async def create_activity(
    request: CreateActivityRequest,
    service: ActivityService = Depends(get_activity_service),
    payload: Payload = Depends(verify_token),
):
    res = await service.create_activity(request)

    response = PaginatedResponse(
        items=res["items"],
        page=res["page"],
        pageSize=res["page_size"],
        total=res["total"],
    )

    return response
