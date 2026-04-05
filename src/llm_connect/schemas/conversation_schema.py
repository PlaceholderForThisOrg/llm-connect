from pydantic import BaseModel


class PostMessageRequest(BaseModel):
    content: str


class PostMessageResponse(BaseModel):
    content: str
