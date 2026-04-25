from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.schemas.activity_schema import CreateActivityRequest


class ActivityService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
        self.repo = activity_repo

    async def create_activity(self, data: CreateActivityRequest):
        activity = await self.repo.create_activity(data)

        return activity

    def get_activity(self, activity_id):
        return self.activity_repo.get_activity_by_id(activity_id)

    def get_activities(self):
        return self.activity_repo.get_activities()
