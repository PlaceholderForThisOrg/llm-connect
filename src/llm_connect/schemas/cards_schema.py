from uuid import UUID

from pydantic import BaseModel


class AddCardRequest(BaseModel):
    front: str
    back: str


class AddCardResponse(BaseModel):
    id: UUID
    front: str
    back: str
