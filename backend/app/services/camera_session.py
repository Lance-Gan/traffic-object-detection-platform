from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import utc_now
from app.db.session import SessionLocal
from app.models import (
    DetectionJob,
    DetectionJobStatus,
    DetectionObject,
    DetectionSourceType,
)
from app.repositories.detection_repository import (
    DetectionRepository,
)
from app.services.camera_types import (
    CameraSessionAccumulator,
)


@dataclass(frozen=True, slots=True)
class ClaimedCameraSession:
    public_id: str
    confidence_threshold: float


class CameraSessionService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def create(
        self,
        confidence_threshold: float,
    ) -> DetectionJob:
        public_id = str(uuid4())

        threshold = Decimal(str(confidence_threshold)).quantize(Decimal("0.0001"))

        job = DetectionJob(
            public_id=public_id,
            source_type=(DetectionSourceType.CAMERA),
            status=(DetectionJobStatus.PENDING),
            original_filename=("Browser camera session"),
            stored_filename=(f"camera-{public_id}"),
            result_filename=None,
            mime_type=("application/x-browser-camera"),
            file_size_bytes=0,
            model_name=settings.model_name,
            device="pending",
            confidence_threshold=threshold,
            total_frames=None,
            processed_frames=0,
            detected_object_count=0,
            unique_object_count=0,
            progress_percent=0,
            duration_ms=None,
            video_duration_ms=None,
            error_message=None,
        )

        self.session.add(job)

        try:
            self.session.commit()
            self.session.refresh(job)
        except Exception:
            self.session.rollback()
            raise

        return job

    @staticmethod
    def claim(
        public_id: str,
    ) -> ClaimedCameraSession | None:
        with SessionLocal() as session:
            repository = DetectionRepository(session)

            job = repository.get_by_public_id(public_id)

            if (
                job is None
                or job.source_type != DetectionSourceType.CAMERA
                or job.status != DetectionJobStatus.PENDING
            ):
                return None

            job.status = DetectionJobStatus.PROCESSING

            job.device = "loading"

            session.commit()

            return ClaimedCameraSession(
                public_id=job.public_id,
                confidence_threshold=float(job.confidence_threshold),
            )

    @staticmethod
    def update_device(
        public_id: str,
        device: str,
    ) -> None:
        with SessionLocal() as session:
            repository = DetectionRepository(session)

            job = repository.get_by_public_id(public_id)

            if job is None:
                return

            job.device = device
            session.commit()

    @staticmethod
    def finish(
        public_id: str,
        accumulator: CameraSessionAccumulator,
        error_message: str | None,
    ) -> None:
        with SessionLocal() as session:
            repository = DetectionRepository(session)

            job = repository.get_by_public_id(public_id)

            if job is None:
                return

            if job.status in {
                DetectionJobStatus.COMPLETED,
                DetectionJobStatus.FAILED,
            }:
                return

            stored_objects = [
                DetectionObject(
                    job_id=job.id,
                    frame_index=(track.first_seen_frame),
                    track_id=track.track_id,
                    class_id=track.class_id,
                    class_name=track.class_name,
                    confidence=Decimal(f"{track.confidence:.5f}"),
                    x1=track.x1,
                    y1=track.y1,
                    x2=track.x2,
                    y2=track.y2,
                )
                for track in accumulator.unique_tracks.values()
            ]

            session.add_all(stored_objects)

            job.total_frames = accumulator.processed_frames

            job.processed_frames = accumulator.processed_frames

            job.detected_object_count = accumulator.total_detections

            job.unique_object_count = len(accumulator.unique_tracks)

            job.duration_ms = accumulator.elapsed_ms()

            job.progress_percent = 100
            job.completed_at = utc_now()

            if error_message is None:
                job.status = DetectionJobStatus.COMPLETED

                job.error_message = None
            else:
                job.status = DetectionJobStatus.FAILED

                job.error_message = error_message[:2000]

            try:
                session.commit()
            except Exception:
                session.rollback()
                raise
