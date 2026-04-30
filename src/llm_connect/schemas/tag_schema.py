from typing import List

from pydantic import BaseModel, ConfigDict


class CreateTagRequest(BaseModel):
    name: str


class CreateTagResponse(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class GetAllTagRequest(BaseModel):
    None


class GetAllTagResponse(BaseModel):
    items: List[CreateTagResponse]
    total: int
    page: int
    pageSize: int
