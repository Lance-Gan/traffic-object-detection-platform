from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.detection_job import DetectionJob


class DetectionObject(TimestampMixin, Base):
    __tablename__ = "detection_objects"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="confidence_range",
        ),
        CheckConstraint(
            "x1 >= 0 AND y1 >= 0 AND x2 >= x1 AND y2 >= y1",
            name="bounding_box_coordinates",
        ),
        Index(
            "ix_detection_objects_job_id",
            "job_id",
        ),
        Index(
            "ix_detection_objects_job_class",
            "job_id",
            "class_name",
        ),
        Index(
            "ix_detection_objects_job_frame",
            "job_id",
            "frame_index",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    job_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "detection_jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    frame_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    track_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    class_id: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    class_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    confidence: Mapped[Decimal] = mapped_column(
        Numeric(6, 5),
        nullable=False,
    )

    x1: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    y1: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    x2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    y2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    job: Mapped[DetectionJob] = relationship(
        back_populates="objects",
    )
