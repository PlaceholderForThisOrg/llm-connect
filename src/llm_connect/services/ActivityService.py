from typing import List, Optional

from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.schemas.activity_schema import CreateActivityRequest


class ActivityService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
        self.repo = activity_repo

    async def create_activity(self, data: CreateActivityRequest):
        activity = await self.repo.create_activity(data)

        return activity

    async def get_activities_v2(
        self,
        page: int,
        page_size: int,
        title: Optional[str],
        tags: Optional[List[str]],
        difficulty: Optional[str],
        type_: Optional[str],
    ):
        activities, total = await self.repo.get_activities_v2(
            page=page,
            page_size=page_size,
            title=title,
            tags=tags,
            difficulty=difficulty,
            type_=type_,
        )

        return {
            "items": activities,
            "page": page,
            "page_size": page_size,
            "total": total,
        }

    async def get_activity(self, activity_id):
        return await self.activity_repo.get_by_id(activity_id)

    def get_activities(self):
        return self.activity_repo.get_activities()
