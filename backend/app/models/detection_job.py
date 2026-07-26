from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.detection_object import DetectionObject


class DetectionSourceType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    CAMERA = "camera"


class DetectionJobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DetectionJob(TimestampMixin, Base):
    __tablename__ = "detection_jobs"
    __table_args__ = (
        CheckConstraint(
            "file_size_bytes >= 0",
            name="file_size_non_negative",
        ),
        CheckConstraint(
            "confidence_threshold >= 0 AND confidence_threshold <= 1",
            name="confidence_threshold_range",
        ),
        CheckConstraint(
            "detected_object_count >= 0",
            name="detected_object_count_non_negative",
        ),
        CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="progress_percent_range",
        ),
        CheckConstraint(
            "unique_object_count >= 0",
            name="unique_object_count_non_negative",
        ),
        Index(
            "ix_detection_jobs_status_created_at",
            "status",
            "created_at",
        ),
        Index(
            "ix_detection_jobs_created_at",
            "created_at",
        ),
        Index(
            "ix_detection_jobs_source_created_at",
            "source_type",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    public_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )

    source_type: Mapped[DetectionSourceType] = mapped_column(
        SQLAlchemyEnum(
            DetectionSourceType,
            name="detection_source_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
    )

    status: Mapped[DetectionJobStatus] = mapped_column(
        SQLAlchemyEnum(
            DetectionJobStatus,
            name="detection_job_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
        default=DetectionJobStatus.PENDING,
        server_default=DetectionJobStatus.PENDING.value,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    result_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    device: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    confidence_threshold: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        default=Decimal("0.2500"),
        server_default=text("0.2500"),
    )

    total_frames: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    processed_frames: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    detected_object_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    objects: Mapped[list[DetectionObject]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DetectionObject.id",
    )
    celery_task_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
    )

    progress_percent: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
    )

    unique_object_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    video_duration_ms: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
