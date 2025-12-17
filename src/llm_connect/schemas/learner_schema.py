from datetime import date
from typing import Optional

from pydantic import BaseModel


class LearnerUpdateRequest(BaseModel):
    name: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    settings: Optional[dict] = None


class LearnerUpdateResponse(BaseModel):
    user_id: str
    name: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    date_of_birth: Optional[date]
    settings: Optional[dict]


class UploadAvatarResponse(BaseModel):
    user_id: str
    avatar_url: str


class GetLearnerRequest(BaseModel):
    None


class GetLearnerResponse(BaseModel):
    user_id: str
    name: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    date_of_birth: Optional[date]
    settings: Optional[dict]
