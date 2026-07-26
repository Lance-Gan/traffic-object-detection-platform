from decimal import Decimal

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import DetectionProcessingError
from app.db.base import utc_now
from app.models import (
    DetectionJob,
    DetectionJobStatus,
    DetectionObject,
    DetectionSourceType,
)
from app.repositories.detection_repository import (
    DetectionRepository,
)
from app.services.file_storage import (
    FileStorageService,
    get_file_storage_service,
)
from app.services.object_detector import (
    ObjectDetector,
    get_object_detector,
)


class ImageDetectionService:
    def __init__(
        self,
        session: Session,
        storage: FileStorageService,
        detector: ObjectDetector,
    ) -> None:
        self.session = session
        self.storage = storage
        self.detector = detector
        self.repository = DetectionRepository(session)

    def process(
        self,
        upload: UploadFile,
        confidence_threshold: float,
    ) -> DetectionJob:
        stored_image = self.storage.save_image(upload)

        normalized_threshold = Decimal(str(confidence_threshold)).quantize(Decimal("0.0001"))

        job = DetectionJob(
            source_type=DetectionSourceType.IMAGE,
            status=DetectionJobStatus.PROCESSING,
            original_filename=stored_image.original_filename,
            stored_filename=stored_image.stored_filename,
            mime_type=stored_image.mime_type,
            file_size_bytes=stored_image.size_bytes,
            model_name=self.detector.model_name,
            device=self.detector.device,
            confidence_threshold=normalized_threshold,
            detected_object_count=0,
        )

        self.repository.add(job)

        try:
            self.session.commit()
            self.session.refresh(job)
        except Exception:
            self.session.rollback()
            self.storage.delete_file(stored_image.path)
            raise

        result_path = settings.result_dir / f"{job.public_id}.jpg"

        try:
            run_result = self.detector.detect_image(
                input_path=stored_image.path,
                output_path=result_path,
                confidence_threshold=confidence_threshold,
            )

            detection_objects = [
                DetectionObject(
                    job_id=job.id,
                    frame_index=0,
                    track_id=None,
                    class_id=item.class_id,
                    class_name=item.class_name,
                    confidence=item.confidence,
                    x1=item.x1,
                    y1=item.y1,
                    x2=item.x2,
                    y2=item.y2,
                )
                for item in run_result.objects
            ]

            self.session.add_all(detection_objects)

            job.status = DetectionJobStatus.COMPLETED
            job.result_filename = run_result.result_filename
            job.detected_object_count = len(detection_objects)
            job.progress_percent = 100
            job.unique_object_count = len(detection_objects)
            job.duration_ms = run_result.duration_ms
            job.completed_at = utc_now()
            job.error_message = None

            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            result_path.unlink(missing_ok=True)
            self._mark_job_failed(
                public_id=job.public_id,
                error=exc,
            )

            raise DetectionProcessingError("Image detection could not be completed") from exc

        completed_job = self.repository.get_by_public_id(job.public_id)

        if completed_job is None:
            raise DetectionProcessingError("The completed detection job could not be loaded")

        return completed_job

    def _mark_job_failed(
        self,
        public_id: str,
        error: Exception,
    ) -> None:
        try:
            failed_job = self.repository.get_by_public_id(public_id)

            if failed_job is None:
                return

            failed_job.status = DetectionJobStatus.FAILED
            failed_job.completed_at = utc_now()
            failed_job.error_message = (f"{type(error).__name__}: {error}")[:2000]

            self.session.commit()
        except Exception:
            self.session.rollback()


def create_image_detection_service(
    session: Session,
) -> ImageDetectionService:
    return ImageDetectionService(
        session=session,
        storage=get_file_storage_service(),
        detector=get_object_detector(),
    )
