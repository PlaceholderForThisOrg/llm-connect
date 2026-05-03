from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_activity_service
from llm_connect.schemas.activity_schema import (
    ActivityUpdate,
    CreateNewActivityRequest,
)
from llm_connect.services.ActivityService import ActivityService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/activities", tags=["Activities"])


@router.patch("/{id}")
async def update_activity(
    id: str,
    payload: ActivityUpdate,
    service: ActivityService = Depends(get_activity_service),
):
    updated_activity = await service.patch_activity(
        id,
        payload,
    )
    return updated_activity


@router.delete("/{id}")
async def delete_activity(
    id: str,
    service: ActivityService = Depends(get_activity_service),
):
    await service.delete_activity(id)
    return {"deleted": id}


@router.get("/recommendation")
async def recommend_activities(
    service: ActivityService = Depends(get_activity_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = payload["sub"]

    res = await service.recommend(learner_id)

    response = res

    return response


@router.get("/{activity_id}")
async def get_activity(
    activity_id: str,
    service: ActivityService = Depends(get_activity_service),
):
    res = await service.get_activity(activity_id)

    # response = GetActivityResponse(
    #     activityId=activity_id,
    #     type=res["type"],
    #     title=res["title"],
    #     metadata=res["metadata"],
    #     goals=res["goals"],
    # )

    response = res

    return response


# @router.get("/")
# def get_activities(
#     a_s: ActivityService = Depends(get_activity_service),
# ):
#     activities = a_s.get_activities()


#     return activities
@router.get("/")
async def search_activities(
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
    request: CreateNewActivityRequest,
    service: ActivityService = Depends(get_activity_service),
    payload: Payload = Depends(verify_token),
):
    # learner_id = payload["sub"]
    res = await service.create_activity_v2(request)

    # Why Paginated happens here?
    # response = PaginatedResponse(
    #     items=res["items"],
    #     page=res["page"],
    #     pageSize=res["page_size"],
    #     total=res["total"],
    # )

    response = res

    return response
