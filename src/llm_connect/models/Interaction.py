import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UUID, DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models import Progress


class Interaction(Base):
    __tablename__ = "interaction"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relationship
    progress_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("progress.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    progress: Mapped["Progress"] = relationship(back_populates="interactions")

    attempt: Mapped[int] = mapped_column(nullable=False)
    input: Mapped[dict] = mapped_column(JSONB)
    output: Mapped[dict] = mapped_column(JSONB)
    is_correct: Mapped[bool] = mapped_column(nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
