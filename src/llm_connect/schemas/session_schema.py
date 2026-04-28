from typing import List

from pydantic import BaseModel


class SubmitInteraction(BaseModel):
    type: str
    interaction: str | List[str]


class Interaction(BaseModel):
    sessionId: str
    type: str = None
    of: str = None
    content: str
    timestamp: str = None


class CreateSessionRequest(BaseModel):
    learnerId: str
    activityId: str


class CreateSessionResponse(BaseModel):
    sessionId: str = None
    conId: str = None


class GetGoalResponse(BaseModel):
    sessionId: str = None
    activityId: str = None
    goal: dict = None
    status: str = None
