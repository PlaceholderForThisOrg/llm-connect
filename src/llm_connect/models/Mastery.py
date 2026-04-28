from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llm_connect.models.Base import Base


class Mastery(Base):
    __tablename__ = "mastery"

    # Composite PK
    learner_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("learner.user_id"),
        primary_key=True,
    )

    learner = relationship("Learner", back_populates="mastery_records")

    atomic_point_id: Mapped[str] = mapped_column(
        String, ForeignKey("atomic_point.id"), primary_key=True
    )

    atomic_point = relationship("AtomicPoint", back_populates="mastery_records")

    # core probability
    p_l: Mapped[float] = mapped_column(Float, nullable=False)

    # for progress
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # time tracking
    first_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # level
    mastery_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # relationship
    # atomic_point = relationship("AtomicPoint")

    # simple constraint
    __table_args__ = (CheckConstraint("p_L >= 0 AND p_L <= 1", name="chk_p_L_range"),)
