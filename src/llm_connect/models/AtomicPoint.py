from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.AtomicPointTag import AtomicPointTag
from llm_connect.models.Base import Base


class AtomicPoint(Base):
    __tablename__ = "atomic_point"

    id: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    examples: Mapped[Optional[str]] = mapped_column(nullable=True)
    level: Mapped[str] = mapped_column(nullable=False)
    popularity: Mapped[Optional[float]] = mapped_column(nullable=True)

    # 🔥 relationship to association
    atomic_point_tags: Mapped[List["AtomicPointTag"]] = relationship(
        back_populates="atomic_point",
        cascade="all, delete-orphan",
    )
