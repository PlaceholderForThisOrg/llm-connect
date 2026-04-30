import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models import AtomicPoint


class AtomicPointRelation(Base):
    __tablename__ = "atomic_point_relation"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    from_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("atomic_point.id"), nullable=False
    )

    to_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("atomic_point.id"), nullable=False
    )

    relation_type: Mapped[str] = mapped_column(nullable=False)

    weight: Mapped[float] = mapped_column(default=1.0)

    # back references
    from_point: Mapped["AtomicPoint"] = relationship(
        "AtomicPoint",
        foreign_keys=[from_id],
        back_populates="outgoing_relations",
    )

    # back references
    to_point: Mapped["AtomicPoint"] = relationship(
        "AtomicPoint",
        foreign_keys=[to_id],
        back_populates="incoming_relations",
    )
