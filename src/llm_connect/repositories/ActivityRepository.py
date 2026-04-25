import uuid

from llm_connect.models.Activity import Activity
from llm_connect.proto.activity.activities_v5 import activities_v5
from llm_connect.schemas.activity_schema import CreateActivityRequest


class ActivityRepository:
    def __init__(self):
        pass

    async def create_activity(self, data: CreateActivityRequest) -> Activity:
        activity = Activity(**data.model_dump())
        # id = str(uuid.uuid4())
        # activity.id = id
        await activity.insert()
        return activity

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
