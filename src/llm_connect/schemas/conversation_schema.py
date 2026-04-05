from pydantic import BaseModel


class PostMessageRequest(BaseModel):
    content: str


class PostMessageResponse(BaseModel):
    content: str


class PostConRequest(BaseModel):
    type: str


class PostConResponse(BaseModel):
    conId: str


class GetHelpResponse(BaseModel):
    content: str


# class GetHelpRequest(BaseModel):
#     ses_id: str
