from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING, Optional
from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models.AtomicPointTag import AtomicPointTag


class AtomicPoint(Base):
    __tablename__ = "atomic_point"

    id: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    examples: Mapped[Optional[str]] = mapped_column(nullable=True)
    level: Mapped[str] = mapped_column(nullable=False)
    popularity: Mapped[Optional[float]] = mapped_column(nullable=True)

    atomic_point_tags: Mapped[List["AtomicPointTag"]] = relationship(
        "AtomicPointTag",
        back_populates="atomic_point",
        cascade="all, delete-orphan",
    )