from typing import List, Optional

from llm_connect.models import Activity
from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.schemas.activity_schema import (
    CreateActivityRequest,
    CreateNewActivityRequest,
)
from llm_connect.services.core.Adapter import Adapter


class ActivityService:
    def __init__(
        self,
        activity_repo: ActivityRepository,
        adapter: Adapter,
        learner_repo: LearnerRepository,
        ap_repo: AtomicPointRepository,
    ):
        self.activity_repo = activity_repo
        self.repo = activity_repo
        self.adapter = adapter
        self.learner_repo = learner_repo
        self.ap_repo = ap_repo

    async def delete_activity(self, activity_id: str):
        activity = await self.repo.get_by_id(activity_id)

        if not activity:
            raise ValueError("Activity not found")

        await self.repo.delete(activity)

    async def create_activity_v2(
        self,
        request: CreateNewActivityRequest,
    ) -> Activity:
        # list to dict
        task_dict = {task.id: task for task in request.tasks}

        # new_request = {
        #     **request.model_dump(),
        #     "task_count": len(task_dict),
        # }

        meta = request.metadata.model_dump()
        meta["task_count"] = len(task_dict)

        # simple validation
        for task_id in request.start_tasks:
            if task_id not in task_dict:
                raise ValueError(f"start_task '{task_id}' not found")

        for task in request.tasks:
            for next_id in task.next_possibles:
                if next_id not in task_dict:
                    raise ValueError(f"Invalid next task reference: {next_id}")

        activity = Activity(
            metadata=meta,
            start_tasks=request.start_tasks,
            tasks=task_dict,
        )

        return await self.repo.create_activity_v2(activity)

    async def recommend(self, learner_id: str):
        learner = await self.learner_repo.get_by_id(learner_id)

        atomic_points = await self.ap_repo.get_all_atomic_points()

        activities = await self.activity_repo.get_all_activities()

        recommended = self.adapter.recommend_activities(
            learner, atomic_points=atomic_points, activities=activities, top_k=10
        )

        return recommended

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
        activity = await self.activity_repo.get_by_id(activity_id)
        if not activity:
            raise ValueError(f"No activity with id: {activity_id}")

        return activity

    def get_activities(self):
        return self.activity_repo.get_activities()
