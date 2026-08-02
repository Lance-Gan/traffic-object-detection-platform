from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.detection_job import (
    DetectionJobStatus,
)


class CameraSessionCreateRequest(BaseModel):
    confidence_threshold: float = Field(
        default=0.25,
        ge=0.01,
        le=1.0,
    )


class CameraSessionCreateResponse(BaseModel):
    public_id: UUID
    status: DetectionJobStatus

    websocket_path: str

    target_fps: int = Field(
        ge=1,
        le=30,
    )

    frame_width: int = Field(
        ge=160,
        le=1920,
    )

    jpeg_quality: float = Field(
        gt=0,
        le=1,
    )

    max_frame_bytes: int = Field(gt=0)
    max_session_seconds: int = Field(gt=0)


class CameraBoundingBoxResponse(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class CameraObjectResponse(BaseModel):
    track_id: int | None

    class_id: int
    class_name: str
    confidence: float = Field(
        ge=0,
        le=1,
    )

    bounding_box: CameraBoundingBoxResponse


class CameraSessionMetricsResponse(BaseModel):
    processed_frames: int = Field(ge=0)
    total_detections: int = Field(ge=0)
    unique_objects: int = Field(ge=0)
    elapsed_ms: int = Field(ge=0)


class CameraLoadingMessage(BaseModel):
    type: Literal["loading_model"]
    message: str


class CameraReadyMessage(BaseModel):
    type: Literal["ready"]

    device: str
    model_name: str

    target_fps: int
    max_session_seconds: int


class CameraFrameMessage(BaseModel):
    type: Literal["frame_result"]

    frame_index: int = Field(ge=0)
    frame_width: int = Field(gt=0)
    frame_height: int = Field(gt=0)

    inference_ms: int = Field(ge=0)
    server_fps: float = Field(ge=0)

    objects: list[CameraObjectResponse]
    summary: dict[str, int]

    session: CameraSessionMetricsResponse


class CameraErrorMessage(BaseModel):
    type: Literal["error"]

    message: str
    fatal: bool


class CameraPongMessage(BaseModel):
    type: Literal["pong"]


class CameraCompletedMessage(BaseModel):
    type: Literal["session_completed"]

    public_id: UUID
    stop_reason: str

    processed_frames: int = Field(ge=0)
    total_detections: int = Field(ge=0)
    unique_objects: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
