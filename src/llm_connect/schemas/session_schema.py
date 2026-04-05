from pydantic import BaseModel


class Interaction(BaseModel):
    sessionId: str
    type: str = None
    of: str = None
    content: str
    timestamp: str = None


class CreateSessionRequest(BaseModel):
    dump: str = None


class CreateSessionResponse(BaseModel):
    activityId: str


class GetGoalResponse(BaseModel):
    sessionId: str = None
    activityId: str = None
    goal: dict = None
    status: str = None
