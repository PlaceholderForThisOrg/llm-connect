import uuid
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    learner_id: Mapped[str] = mapped_column(
        String, ForeignKey("learner.user_id"), nullable=False
    )

    type: Mapped[str] = mapped_column(String, nullable=True)

    title: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_ad: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    # relationship with messages
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )

    # relationship with Learner
    learner: Mapped["Learner"] = relationship(back_populates="conversations")
