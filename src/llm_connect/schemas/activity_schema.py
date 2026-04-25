from typing import Annotated, Dict, List, Literal, Union

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class GetActivityResponse(BaseModel):
    activityId: str
    type: str = None
    title: str = None
    metadata: dict = None
    difficulty: str = None
    estimatedTime: int = None
    goals: dict = None


class BaseTask(BaseModel):
    id: str
    type: str
    atomic_points: List[str]
    next_possibles: List[str]


class GenerateTask(BaseTask):
    type: Literal["generate"]
    prompt: str


class SelectTask(BaseTask):
    type: Literal["select"]
    question: str
    answers: List[str]
    correct: List[str]


Task = Annotated[Union[GenerateTask, SelectTask], Field(discriminator="type")]


class Metadata(BaseModel):
    type: str
    title: str
    description: str
    general_difficulty: str
    estimated_time: int
    tags: List[str] = Field(default_factory=list)


class CreateActivityRequest(BaseModel):

    metadata: Metadata

    start_tasks: List[str]

    tasks: Dict[str, Task]


class CreateActivityResponse(BaseModel):
    None


class GetAllActivityResponse(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    metadata: Metadata

    class Config:
        populate_by_name = True
