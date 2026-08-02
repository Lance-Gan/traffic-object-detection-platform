from datetime import datetime

from pydantic import BaseModel, Field

from app.models.detection_job import (
    DetectionJobStatus,
    DetectionSourceType,
)


class BoundingBoxResponse(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionObjectResponse(BaseModel):
    frame_index: int = Field(
        ge=0,
    )

    track_id: int | None

    class_id: int
    class_name: str
    confidence: float

    bounding_box: BoundingBoxResponse


class DetectionJobSummaryResponse(BaseModel):
    public_id: str
    source_type: DetectionSourceType
    status: DetectionJobStatus
    original_filename: str
    result_url: str | None
    detected_object_count: int
    duration_ms: int | None
    summary: dict[str, int]
    created_at: datetime
    completed_at: datetime | None
    progress_percent: int = Field(
        ge=0,
        le=100,
    )

    unique_object_count: int = Field(
        ge=0,
    )

    total_frames: int | None
    processed_frames: int | None


class DetectionJobDetailResponse(DetectionJobSummaryResponse):
    model_name: str
    device: str
    confidence_threshold: float
    file_size_bytes: int
    objects: list[DetectionObjectResponse]
    video_duration_ms: int | None


class DetectionJobListResponse(BaseModel):
    items: list[DetectionJobSummaryResponse]

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)

    count: int = Field(ge=0)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)

    has_previous: bool
    has_next: bool
