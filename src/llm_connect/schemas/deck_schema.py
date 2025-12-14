from datetime import datetime

from pydantic import BaseModel


class CreateDeckRequest(BaseModel):
    name: str
    description: str
    is_shared: bool


class CreateDeckResponse(BaseModel):
    id: int
    name: str
    description: str
    is_shared: bool


class DeleteDeckRequest(BaseModel):
    None


class DeleteDeckResponse(BaseModel):
    id: int
    name: str
    description: str
    is_shared: bool


class GetDeckSummary(BaseModel):
    id: int
    name: str
    description: str
    is_shared: bool


class GetDeckDetail(BaseModel):
    id: int
    name: str
    description: str
    is_shared: bool
    created_at: datetime
