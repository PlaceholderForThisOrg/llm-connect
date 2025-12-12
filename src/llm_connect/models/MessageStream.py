from enum import Enum

from pydantic import BaseModel


class Role(Enum):
    LEARNER = "LEARNER"
    COMPANION = "COMPANION"


class MessageStream(BaseModel):
    user_id: str
    role: str
    content: str
    timestamp: str
