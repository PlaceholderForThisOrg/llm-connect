from typing import Annotated, Dict, List, Literal, Union

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


class MetaData(BaseModel):
    type: str
    title: str
    description: str
    general_difficulty: str
    estimated_time: int


class CreateActivityRequest(BaseModel):

    metadata: MetaData

    start_tasks: List[str]

    tasks: Dict[str, Task]


class CreateActivityResponse(BaseModel):
    None
