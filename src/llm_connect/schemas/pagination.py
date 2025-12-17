from typing import Generic, List, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    type: Literal["offset"] = "offset"
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_more: bool
    next_cursor: None = None


class ListResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="1-based page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
