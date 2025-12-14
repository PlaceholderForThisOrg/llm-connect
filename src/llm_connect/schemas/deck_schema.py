from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
