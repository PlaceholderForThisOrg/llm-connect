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
