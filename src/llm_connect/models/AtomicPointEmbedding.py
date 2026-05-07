import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models.AtomicPoint import AtomicPoint


class AtomicPointEmbedding(Base):
    __tablename__ = "atomic_point_embedding"

    atomic_point_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("atomic_point.id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding_model: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_dims: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    semantic_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    embedding: Mapped[list] = mapped_column(VECTOR(768), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    atomic_point: Mapped["AtomicPoint"] = relationship(
        "AtomicPoint",
        back_populates="embedding_row",
    )
