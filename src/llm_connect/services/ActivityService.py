from llm_connect.repositories.ActivityRepository import ActivityRepository


class ActivityService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo

    def get_activity(self, activity_id):
        return self.activity_repo.get_activity_by_id(activity_id)

    def get_activities(self):
        return self.activity_repo.get_activities()
