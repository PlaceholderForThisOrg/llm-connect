import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    learnerId: str
    title: Optional[str] = None
    type: Optional[str] = None


# FIXME: skip by now
class CreateConversationResponse(BaseModel):
    id: uuid.UUID
    learnerId: str
    title: Optional[str]
    type: Optional[str]
    createdAt: datetime

    class Config:
        from_attributes = True


class PostMessageRequest(BaseModel):
    content: str


class PostMessageResponse(BaseModel):
    content: str


class PostConRequest(BaseModel):
    type: str


class PostConResponse(BaseModel):
    conId: str


class GetHelpResponse(BaseModel):
    content: str


# class GetHelpRequest(BaseModel):
#     ses_id: str
