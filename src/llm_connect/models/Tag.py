from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.AtomicPointTag import AtomicPointTag
from llm_connect.models.Base import Base


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    # 🔥 relationship to association
    atomic_point_tags: Mapped[List["AtomicPointTag"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
    )
