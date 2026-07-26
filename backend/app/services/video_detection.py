from decimal import Decimal

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    DetectionJob,
    DetectionJobStatus,
    DetectionSourceType,
)
from app.services.video_storage import (
    VideoStorageService,
    get_video_storage_service,
)
from app.tasks.video import (
    process_video_job,
)


class VideoDetectionService:
    def __init__(
        self,
        session: Session,
        storage: VideoStorageService,
    ) -> None:
        self.session = session
        self.storage = storage

    def create_job(
        self,
        upload: UploadFile,
        confidence_threshold: float,
    ) -> DetectionJob:
        stored_video = self.storage.save_video(upload)

        threshold = Decimal(str(confidence_threshold)).quantize(Decimal("0.0001"))

        job = DetectionJob(
            source_type=(DetectionSourceType.VIDEO),
            status=(DetectionJobStatus.PENDING),
            original_filename=(stored_video.original_filename),
            stored_filename=(stored_video.stored_filename),
            mime_type=(stored_video.mime_type),
            file_size_bytes=(stored_video.size_bytes),
            model_name=settings.model_name,
            device="pending",
            confidence_threshold=(threshold),
            total_frames=(stored_video.frame_count),
            processed_frames=0,
            detected_object_count=0,
            unique_object_count=0,
            progress_percent=0,
            video_duration_ms=round(stored_video.duration_seconds * 1000),
        )

        self.session.add(job)

        try:
            self.session.commit()
            self.session.refresh(job)

            task_result = process_video_job.delay(job.public_id)

            job.celery_task_id = task_result.id

            self.session.commit()

            return job
        except Exception:
            self.session.rollback()

            self.storage.delete_file(stored_video.path)

            raise


def create_video_detection_service(
    session: Session,
) -> VideoDetectionService:
    return VideoDetectionService(
        session=session,
        storage=(get_video_storage_service()),
    )
