from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    attempt: int
    input: dict
    output: dict
    is_correct: bool
    score: Optional[float]
    created_at: datetime


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: str
    status: str
    num_attempts: int
    score: Optional[float]

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    interactions: List[InteractionResponse]


class GetSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    activity_id: str
    status: str
    progress: Optional[float]
    score: Optional[float]

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    current_task: str

    progresses: List[ProgressResponse]


class GetAllSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    activity_id: str
    status: str
    progress: Optional[float]
    score: Optional[float]

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    current_task: str


class SessionSearchQuery(BaseModel):
    activity_id: Optional[str] = None
    status: Optional[str] = None
    learner_id: Optional[str] = None

    started_from: Optional[datetime] = None
    started_to: Optional[datetime] = None

    min_score: Optional[float] = None
    max_score: Optional[float] = None

    page: int = 1
    page_size: int = 20


class GenerateAnswer(BaseModel):
    response: str = None


class SelectAnswer(BaseModel):
    selected: List[str] = None


class FillAnswer(BaseModel):
    filled: List[str] = None


class MatchAnswer(BaseModel):
    matched: Dict[str | int, str | int]


class ReorderAnswer(BaseModel):
    reordered: List[str | int]


class SubmitInteraction(BaseModel):
    type: str
    interaction: str | List[str] = None
    answer: Union[
        GenerateAnswer,
        SelectAnswer,
        FillAnswer,
        MatchAnswer,
        ReorderAnswer,
    ] = None


class Interaction(BaseModel):
    sessionId: str
    type: str = None
    of: str = None
    content: str
    timestamp: str = None


class CreateSessionRequest(BaseModel):
    # learnerId: str
    activityId: str


class CreateSessionResponse(BaseModel):
    sessionId: str = None
    conId: str = None


class GetGoalResponse(BaseModel):
    sessionId: str = None
    activityId: str = None
    goal: dict = None
    status: str = None
