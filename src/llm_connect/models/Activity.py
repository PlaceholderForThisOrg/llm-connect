from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from beanie import Document
from pydantic import BaseModel, Field

# class Task(BaseModel):
#     id: str
#     type: TaskType

#     objective: str = None

#     prompt: str = None

#     solution: dict = None

#     answer: Union[
#         GenerateAnswer, SelectAnswer, FillAnswer, MatchAnswer, ReorderAnswer
#     ] = None

#     content: Optional[str] = None
#     options: Optional[List[str]] = None  # for select/match/reorder

#     # optional
#     hints: List[str] = []
#     feedback: dict = {}

#     # progression
#     next_possibles: List[str] = []

#     # immersion context
#     context: Optional[str] = None


# class GenerateTask(BaseTask):
#     type: Literal["generate"]
#     prompt: str


# class SelectTask(BaseTask):
#     type: Literal["select"]
#     question: str
#     answers: List[str]
#     correct: List[str]

# class FillTask(BaseTask):
#     type: Literal["fill"]


# Task = Annotated[Union[GenerateTask, SelectTask], Field(discriminator="type")]


class TaskType(str, Enum):
    GENERATE = "generate"
    SELECT = "select"
    FILL = "fill"
    MATCH = "match"
    REORDER = "reorder"


class BaseTask(BaseModel):
    id: str
    type: TaskType

    prompt: Optional[str] = None
    context: Optional[str] = None

    hints: List[str] = Field(default_factory=list)
    feedback: Dict = Field(default_factory=dict)
    next_possibles: List[str] = Field(default_factory=list)
    atomic_points: List[str] = Field(default_factory=list)


class GenerateTask(BaseTask):
    type: Literal[TaskType.GENERATE]
    sample_answers: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class SelectTask(BaseTask):
    type: Literal[TaskType.SELECT]
    options: Optional[List[str]] = None
    correct_options: Optional[List[str | int]] = None


class FillTask(BaseTask):
    type: Literal[TaskType.FILL]
    correct_answers: Optional[List[str]] = None
    case_sensitive: bool = False


class MatchTask(BaseTask):
    type: Literal[TaskType.MATCH]
    a: Optional[List[str]] = None
    b: Optional[List[str]] = None
    correct_pairs: Optional[Dict[int | str, int | str]] = None


class ReorderTask(BaseTask):
    type: Literal[TaskType.REORDER]
    options: Optional[List[str]] = None
    correct_orders: Optional[List[int | str]] = None


Task = Union[
    GenerateTask,
    SelectTask,
    FillTask,
    MatchTask,
    ReorderTask,
]


class ActivityType(str, Enum):
    ROLE_PLAY = "ROLE_PLAY"
    # EMAIL = "email"
    # ARTICLE = "article"
    READING = "READING"


class Metadata(BaseModel):
    type: str
    title: str
    description: str
    npc: str = None
    general_difficulty: str
    estimated_time: int
    tags: List[str] = Field(default_factory=list)
    media: Optional[List[str]] = None
    content: Optional[str] = None
    task_count: int = None


class Activity(Document):
    metadata: Metadata
    start_tasks: List[str]
    tasks: Dict[str, Task]

    class Settings:
        name = "activity"
