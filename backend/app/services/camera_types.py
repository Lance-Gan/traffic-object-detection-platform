from dataclasses import dataclass, field
from time import perf_counter


@dataclass(frozen=True, slots=True)
class CameraObjectData:
    track_id: int | None

    class_id: int
    class_name: str
    confidence: float

    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class CameraFrameResultData:
    frame_index: int

    frame_width: int
    frame_height: int

    inference_ms: int

    objects: tuple[CameraObjectData, ...]


@dataclass(frozen=True, slots=True)
class TrackSnapshot:
    track_id: int
    first_seen_frame: int

    class_id: int
    class_name: str
    confidence: float

    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(slots=True)
class CameraSessionAccumulator:
    started_at: float = field(default_factory=perf_counter)

    processed_frames: int = 0
    total_detections: int = 0

    unique_tracks: dict[
        int,
        TrackSnapshot,
    ] = field(default_factory=dict)

    def record(
        self,
        result: CameraFrameResultData,
    ) -> None:
        self.processed_frames += 1
        self.total_detections += len(result.objects)

        for detected_object in result.objects:
            track_id = detected_object.track_id

            if track_id is None or track_id in self.unique_tracks:
                continue

            self.unique_tracks[track_id] = TrackSnapshot(
                track_id=track_id,
                first_seen_frame=(result.frame_index),
                class_id=(detected_object.class_id),
                class_name=(detected_object.class_name),
                confidence=(detected_object.confidence),
                x1=detected_object.x1,
                y1=detected_object.y1,
                x2=detected_object.x2,
                y2=detected_object.y2,
            )

    def elapsed_ms(self) -> int:
        return max(
            0,
            round((perf_counter() - self.started_at) * 1000),
        )
