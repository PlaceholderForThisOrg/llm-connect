from pydantic import BaseModel


class CreateTagRequest(BaseModel):
    name: str
