import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models.AtomicPointEmbedding import AtomicPointEmbedding
    from llm_connect.models.AtomicPointRelation import AtomicPointRelation
    from llm_connect.models.AtomicPointTag import AtomicPointTag
    from llm_connect.models.Mastery import Mastery


class AtomicPoint(Base):
    __tablename__ = "atomic_point"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
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

    p_init: Mapped[float] = mapped_column(default=0.2)
    p_learn: Mapped[float] = mapped_column(default=0.1)
    p_guess: Mapped[float] = mapped_column(default=0.2)
    p_slip: Mapped[float] = mapped_column(default=0.1)

    mastery_records: Mapped[List["Mastery"]] = relationship(
        "Mastery",
        back_populates="atomic_point",
        cascade="all, delete-orphan",
    )

    # out relation
    outgoing_relations: Mapped[List["AtomicPointRelation"]] = relationship(
        "AtomicPointRelation",
        foreign_keys="AtomicPointRelation.from_id",
        back_populates="from_point",
        cascade="all, delete-orphan",
    )

    # in relation
    incoming_relations: Mapped[List["AtomicPointRelation"]] = relationship(
        "AtomicPointRelation",
        foreign_keys="AtomicPointRelation.to_id",
        back_populates="to_point",
        cascade="all, delete-orphan",
    )

    embedding_row: Mapped[Optional["AtomicPointEmbedding"]] = relationship(
        "AtomicPointEmbedding",
        back_populates="atomic_point",
        uselist=False,
        cascade="all, delete-orphan",
    )
