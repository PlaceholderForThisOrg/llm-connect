import datetime
from typing import Any, Dict, List

from sqlalchemy import JSON, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models import Conversation
from llm_connect.models.Base import Base


class Learner(Base):

    __tablename__ = "learner"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)

    nickname: Mapped[str] = mapped_column(String, nullable=False)

    avatar_url: Mapped[str] = mapped_column(String, nullable=True)

    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    conversations: Mapped[List["Conversation"]] = relationship(
        back_populates="learner", cascade="all, delete-orphan"
    )
