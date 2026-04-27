from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


# FIXME: return
class ChatResponse(BaseModel):
    message: str
