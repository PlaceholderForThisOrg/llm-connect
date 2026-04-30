from typing import Annotated, Dict, List, Literal, Union

from beanie import Document
from pydantic import BaseModel, Field


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


class Activity(Document):
    # id: str

    metadata: Metadata

    start_tasks: List[str]

    tasks: Dict[str, Task]

    class Settings:
        name = "activity"
