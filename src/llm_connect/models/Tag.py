from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from sqlalchemy import String
from llm_connect.models.Base import Base

if TYPE_CHECKING:
    from llm_connect.models.AtomicPointTag import AtomicPointTag


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    atomic_point_tags: Mapped[List["AtomicPointTag"]] = relationship(
        "AtomicPointTag",
        back_populates="tag",
        cascade="all, delete-orphan"
    )