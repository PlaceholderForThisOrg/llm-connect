from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateDeckRequest(BaseModel):
    name: str
    description: str
    is_shared: bool


class CreateDeckResponse(BaseModel):
    id: UUID
    name: str
    description: str
    is_shared: bool


class DeleteDeckRequest(BaseModel):
    None


class DeleteDeckResponse(BaseModel):
    id: UUID
    name: str
    description: str
    is_shared: bool


class GetDeckSummary(BaseModel):
    id: UUID
    name: str
    description: str
    is_shared: bool


class GetDeckDetail(BaseModel):
    id: UUID
    name: str
    description: str
    is_shared: bool
    created_at: datetime


class GetDeckReviewsParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    # offset: int = Field(default=0, ge=0)


class ReviewCard(BaseModel):
    learner_card_id: UUID
    card_id: UUID
    front: str
    back: str

    state: str
    interval: int
    repetitions: int
    ease_factor: float

    next_review: Optional[datetime]
    last_reviewed: Optional[datetime]


class GetDeckReviewsResponse(BaseModel):
    deck_id: UUID
    total: int
    items: List[ReviewCard]


class SubmitReviewRequest(BaseModel):
    quality: int = Field(ge=0, le=5)


class SubmitReviewResponse(BaseModel):
    learner_card_id: UUID
    state: str
    interval: int
    repetitions: int
    ease_factor: float
    next_review: Optional[datetime]
