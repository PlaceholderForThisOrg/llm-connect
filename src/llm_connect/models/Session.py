import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from llm_connect.models.Base import Base


class Session(Base):
    __tablename__ = "session"

    id: Mapped[uuid.UUID] = mapped_column(
        uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    activity_id: Mapped[str] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(nullable=False)
    progress: float = mapped_column(nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    current_task: Mapped[str] = mapped_column(nullable=False)
    meta: Mapped[Dict[str, Any]] = mapped_column(JSONB)
