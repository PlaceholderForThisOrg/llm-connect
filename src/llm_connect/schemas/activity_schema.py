from typing import Annotated, Dict, List, Literal, Optional, Union

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from llm_connect.models.Activity import (
    FillTask,
    GenerateTask,
    MatchTask,
    ReorderTask,
    SelectTask,
)

TaskRequest = Annotated[
    Union[
        GenerateTask,
        SelectTask,
        FillTask,
        MatchTask,
        ReorderTask,
    ],
    Field(discriminator="type"),
]


class Metadata(BaseModel):
    type: str
    title: str
    description: str
    general_difficulty: str
    estimated_time: int
    tags: List[str] = Field(default_factory=list)
    media: Optional[List[str]] = None
    content: Optional[str] = None


class CreateNewActivityRequest(BaseModel):
    metadata: Metadata
    start_tasks: List[str] = Field(..., description="List of entry task IDs")
    tasks: List[TaskRequest] = Field(
        ..., description="List of tasks (polymorphic by type)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "metadata": {
                    "type": "reading",
                    "title": "All Task Types Example",
                    "description": "An activity containing all 5 task types",
                    "general_difficulty": "medium",
                    "estimated_time": 20,
                    "tags": ["mixed", "demo"],
                },
                "start_tasks": ["task_1"],
                "tasks": [
                    {
                        "id": "task_1",
                        "type": "generate",
                        "prompt": "Describe your favorite food",
                        "sample_answers": ["I love pizza"],
                        "keywords": ["food"],
                        "next_possibles": ["task_2"],
                        "atomic_points": [],
                    },
                    {
                        "id": "task_2",
                        "type": "select",
                        "prompt": "Choose the correct verb",
                        "options": ["is", "are"],
                        "correct_options": ["is"],
                        "next_possibles": ["task_3"],
                        "atomic_points": [],
                    },
                    {
                        "id": "task_3",
                        "type": "fill",
                        "prompt": "I ___ a student",
                        "correct_answers": ["am"],
                        "case_sensitive": False,
                        "next_possibles": ["task_4"],
                        "atomic_points": [],
                    },
                    {
                        "id": "task_4",
                        "type": "match",
                        "prompt": "Match countries to capitals",
                        "a": ["France", "Japan"],
                        "b": ["Paris", "Tokyo"],
                        "correct_pairs": {
                            "France": "Paris",
                            "Japan": "Tokyo",
                        },
                        "next_possibles": ["task_5"],
                        "atomic_points": [],
                    },
                    {
                        "id": "task_5",
                        "type": "reorder",
                        "prompt": "Arrange into correct sentence",
                        "options": ["student", "I", "am", "a"],
                        "correct_orders": ["I am a student"],
                        "next_possibles": [],
                        "atomic_points": [],
                    },
                ],
            }
        }
    }


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
