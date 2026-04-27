import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models import Interaction, Session


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Link with Session
    session: Mapped["Session"] = relationship(back_populates="progresses")

    # Just number
    task_id: Mapped[str] = mapped_column(nullable=False)

    # Progress state
    status: Mapped[str] = mapped_column(nullable=False)
    num_attempts: Mapped[int] = mapped_column(default=0, nullable=True)

    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    interactions: Mapped[List["Interaction"]] = relationship(
        back_populates="progress",
        cascade="all, delete-orphan",
        order_by="Interaction.attempt",
    )
