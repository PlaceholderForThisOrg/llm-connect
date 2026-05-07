import uuid
from typing import List, Optional

from pydantic import BaseModel


class CreateAtomicPointRelationRequest(BaseModel):
    from_id: uuid.UUID
    to_id: uuid.UUID
    relation_type: str
    weight: float = 1.0


class CreateAPRelation(BaseModel):
    to_id: str
    # PREREQUISITE
    # PART-OF
    # SIMILAR
    # EASIER
    relation_type: str
    weight: float = 1.0


class CreateAPRequest(BaseModel):
    type: str
    name: str
    description: str
    examples: str
    level: str
    popularity: float

    # tagIds: List[str] = None
    tags: List[str] = None
    relations: Optional[List["CreateAPRelation"]] = None


class CreateAPResponse(BaseModel):
    id: str
    name: str
    description: str
    examples: str
    level: str
    popularity: float

    tagIds: List[str]


class RAGSearchHit(BaseModel):
    atomic_point_id: uuid.UUID
    name: str
    type: str
    level: str
    cosine_distance: float
    semantic_text: str


class GetAtomicPointResponse(BaseModel):
    id: uuid.UUID
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
