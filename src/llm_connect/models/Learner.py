import datetime
from typing import Dict

from pydantic import BaseModel


class Learner(BaseModel):
    user_id: str
    name: str
    nickname: str
    avatar_url: str
    date_of_birth: datetime.date
    settings: Dict
    created_at: datetime.datetime
    updated_at: datetime.datetime
