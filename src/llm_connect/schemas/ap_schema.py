from typing import List

from pydantic import BaseModel


class CreateAPRequest(BaseModel):
    type: str
    name: str
    description: str
    examples: str
    level: str
    popularity: float

    # tagIds: List[str] = None
    tags: List[str]


class CreateAPResponse(BaseModel):
    id: str
    name: str
    description: str
    examples: str
    level: str
    popularity: float

    tagIds: List[str]


class GetAtomicPointResponse(BaseModel):
    id: str
    name: str
    type: str
    level: str
    popularity: float | None
    tags: List[str]

    @staticmethod
    def from_model(ap):
        return GetAtomicPointResponse(
            id=ap.id,
            name=ap.name,
            type=ap.type,
            level=ap.level,
            popularity=ap.popularity,
            tags=[apt.tag.name for apt in ap.atomic_point_tags],
        )
