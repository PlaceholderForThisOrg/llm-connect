from typing import List

from pydantic import BaseModel


class CreateAPRequest(BaseModel):
    type: str
    name: str
    description: str
    examples: str
    level: str
    popularity: float

    tagIds: List[str]


class CreateAPResponse(BaseModel):
    id: str
    name: str
    description: str
    examples: str
    level: str
    popularity: float

    tagIds: List[str]
