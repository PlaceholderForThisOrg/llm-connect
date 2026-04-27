import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models import Learner, Progress


class Session(Base):
    __tablename__ = "session"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    activity_id: Mapped[str] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(nullable=False)
    progress: Mapped[float] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    current_task: Mapped[str] = mapped_column(nullable=False)

    meta: Mapped[Dict[str, Any]] = mapped_column(JSONB)

    score: Mapped[float] = mapped_column(Float, nullable=True)

    progresses: Mapped[List["Progress"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    # to link with Learner
    learner_id: Mapped[str] = mapped_column(
        ForeignKey("learner.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    learner: Mapped["Learner"] = relationship(back_populates="sessions")
