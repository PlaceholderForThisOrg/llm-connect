from fastapi import APIRouter, Depends

from llm_connect.clients.dependencies import get_activity_service
from llm_connect.schemas.activity_schema import GetActivityResponse
from llm_connect.services.ActivityService import ActivityService

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
    )

    return response
