import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base


class Message(Base):
    __tablename__ = "message"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversation.id"), nullable=False
    )

    role: Mapped[str] = mapped_column(nullable=False)

    content: Mapped[str] = mapped_column(nullable=False)

    meta: Mapped[Dict[str, Any]] = mapped_column(JSONB)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
