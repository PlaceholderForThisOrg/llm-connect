from pydantic import BaseModel


class GetActivityResponse(BaseModel):
    activityId: str
    type: str = None
    title: str = None
    metadata: dict = None
    difficulty: str = None
    estimatedTime: int = None
    goals: dict = None
