from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models.AtomicPoint import AtomicPoint
    from llm_connect.models.Tag import Tag


class AtomicPointTag(Base):
    __tablename__ = "atomicpoint_tag"

    ap_id: Mapped[str] = mapped_column(
        ForeignKey("atomic_point.id"),
        primary_key=True
    )

    tag_id: Mapped[str] = mapped_column(
        ForeignKey("tag.id"),
        primary_key=True
    )

    atomic_point: Mapped["AtomicPoint"] = relationship(
        "AtomicPoint",
        back_populates="atomic_point_tags"
    )

    tag: Mapped["Tag"] = relationship(
        "Tag",
        back_populates="atomic_point_tags"
    )