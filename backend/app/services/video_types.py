from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class VideoDetectionData:
    frame_index: int
    track_id: int | None

    class_id: int
    class_name: str
    confidence: float

    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class VideoTrackSnapshot:
    frame_index: int
    track_id: int

    class_id: int
    class_name: str
    confidence: Decimal

    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class VideoProgressData:
    progress_percent: int
    processed_frames: int
    detection_count: int
    unique_object_count: int


@dataclass(frozen=True, slots=True)
class VideoProcessingResult:
    result_filename: str
    processed_frames: int
    detection_count: int
    duration_ms: int
    device: str

    unique_tracks: tuple[
        VideoTrackSnapshot,
        ...,
    ]
