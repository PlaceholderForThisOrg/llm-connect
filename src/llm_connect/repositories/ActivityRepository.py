from typing import List, Optional

from llm_connect.models.Activity import Activity
from llm_connect.proto.activity.activities_v5 import activities_v5
from llm_connect.schemas.activity_schema import (
    CreateActivityRequest,
    GetAllActivityResponse,
)


class ActivityRepository:
    def __init__(self):
        pass

    async def save(self, activity: Activity) -> Activity:
        await activity.save()
        return activity

    async def delete(self, activity: Activity):
        await activity.delete()

    async def get_all_activities(self) -> List[Activity]:
        return await Activity.find_all().to_list()

    async def get_by_id(self, activity_id: str) -> Optional[Activity]:
        return await Activity.get(activity_id)

    async def create_activity_v2(self, activity: Activity) -> Activity:
        await activity.insert()
        return activity

    async def create_activity(self, data: CreateActivityRequest) -> Activity:
        activity = Activity(**data.model_dump())
        # id = str(uuid.uuid4())
        # activity.id = id
        await activity.insert()
        return activity

    async def get_activities_v2(
        self,
        page: int,
        page_size: int,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        type_: Optional[str] = None,
    ):
        query = {}

        if title:
            query["metadata.title"] = {"$regex": title, "$options": "i"}

        if tags:
            query["metadata.tags"] = {"$in": tags}

        if difficulty:
            query["metadata.general_difficulty"] = difficulty

        if type_:
            query["metadata.type"] = type_

        skip = (page - 1) * page_size

        cursor = Activity.find(query).skip(skip).limit(page_size)

        activities = await cursor.project(GetAllActivityResponse).to_list()
        total = await Activity.find(query).count()

        return activities, total

    def get_activities(
        self,
    ):
        return [v for k, v in activities_v5.items()]

    def get_activity_by_id(self, activity_id: str):
        # FIXME: prototype only
        return activities_v5[activity_id]

    def get_interaction_by_id(self, activity_id: str, interaction_id: str):
        return
        # return activity_v4["interactions"][interaction_id]

    def get_checkpoint_by_id(self, activity_id, checkpoint_id):
        # FIXME: prototype only - in-memory
        return
        # return activity_v4["checkpoints"][checkpoint_id]

    def get_goal_by_id(self, activity_id, goal_id):
        activity = activities_v5[activity_id]
        return activity["goals"][goal_id]
