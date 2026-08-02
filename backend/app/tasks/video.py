from sqlalchemy import (
    delete,
    select,
)
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
from app.services.video_processor import (
    VideoProcessor,
)
from app.services.video_types import (
    VideoProcessingResult,
    VideoProgressData,
)
from app.worker.celery_app import (
    celery_app,
)


@celery_app.task(  # type: ignore[untyped-decorator]
    bind=True,
    name=("app.tasks.video.process_video_job"),
)
def process_video_job(
    self: object,
    public_id: str,
) -> dict[str, object]:
    del self

    try:
        with SessionLocal() as session:
            job = _find_job(
                session,
                public_id,
            )

            if job is None:
                return {
                    "public_id": public_id,
                    "status": "missing",
                }

            if job.source_type != DetectionSourceType.VIDEO:
                raise RuntimeError("The selected job is not a video job")

            if job.status == DetectionJobStatus.COMPLETED and job.result_filename is not None:
                return {
                    "public_id": public_id,
                    "status": "completed",
                }

            input_path = settings.video_upload_dir / job.stored_filename

            if not input_path.is_file():
                raise FileNotFoundError("The uploaded source video could not be found")

            model_name = job.model_name

            confidence_threshold = float(job.confidence_threshold)

            session.execute(delete(DetectionObject).where(DetectionObject.job_id == job.id))

            job.status = DetectionJobStatus.PROCESSING

            job.device = "loading"
            job.progress_percent = 1
            job.processed_frames = 0
            job.detected_object_count = 0
            job.unique_object_count = 0
            job.result_filename = None
            job.completed_at = None
            job.error_message = None

            session.commit()

        processor = VideoProcessor(
            model_name=model_name,
            requested_device=(settings.inference_device),
            target_fps=(settings.video_target_fps),
            tracker_name=(settings.video_tracker_name),
            inference_size=(settings.video_inference_size),
            output_max_width=(settings.video_output_max_width),
        )

        _update_device(
            public_id,
            processor.device,
        )

        result = processor.process(
            input_path=input_path,
            public_id=public_id,
            confidence_threshold=(confidence_threshold),
            progress_callback=lambda progress: _update_progress(
                public_id,
                progress,
            ),
        )

        _complete_job(
            public_id,
            result,
        )

        return {
            "public_id": public_id,
            "status": "completed",
            "result_filename": (result.result_filename),
            "processed_frames": (result.processed_frames),
            "detection_count": (result.detection_count),
            "unique_object_count": len(result.unique_tracks),
        }

    except Exception as exc:
        _mark_failed(
            public_id=public_id,
            error=exc,
        )

        raise


def _find_job(
    session: Session,
    public_id: str,
) -> DetectionJob | None:
    statement = select(DetectionJob).where(DetectionJob.public_id == public_id)

    return session.scalar(statement)


def _update_device(
    public_id: str,
    device: str,
) -> None:
    with SessionLocal() as session:
        job = _find_job(
            session,
            public_id,
        )

        if job is None:
            return

        job.device = device
        session.commit()


def _update_progress(
    public_id: str,
    progress: VideoProgressData,
) -> None:
    with SessionLocal() as session:
        job = _find_job(
            session,
            public_id,
        )

        if job is None:
            return

        if job.status in {
            DetectionJobStatus.COMPLETED,
            DetectionJobStatus.FAILED,
        }:
            return

        job.progress_percent = max(
            job.progress_percent,
            progress.progress_percent,
        )

        job.processed_frames = progress.processed_frames

        job.detected_object_count = progress.detection_count

        job.unique_object_count = progress.unique_object_count

        session.commit()


def _complete_job(
    public_id: str,
    result: VideoProcessingResult,
) -> None:
    with SessionLocal() as session:
        job = _find_job(
            session,
            public_id,
        )

        if job is None:
            raise RuntimeError("The completed video job could not be loaded")

        stored_objects = [
            DetectionObject(
                job_id=job.id,
                frame_index=(track.frame_index),
                track_id=track.track_id,
                class_id=track.class_id,
                class_name=(track.class_name),
                confidence=(track.confidence),
                x1=track.x1,
                y1=track.y1,
                x2=track.x2,
                y2=track.y2,
            )
            for track in result.unique_tracks
        ]

        session.add_all(stored_objects)

        job.status = DetectionJobStatus.COMPLETED

        job.result_filename = result.result_filename

        job.progress_percent = 100

        job.processed_frames = result.processed_frames

        job.detected_object_count = result.detection_count

        job.unique_object_count = len(result.unique_tracks)

        job.duration_ms = result.duration_ms

        job.device = result.device
        job.completed_at = utc_now()
        job.error_message = None

        session.commit()


def _mark_failed(
    public_id: str,
    error: Exception,
) -> None:
    result_path = settings.video_result_dir / f"{public_id}.mp4"

    working_path = settings.video_result_dir / f".{public_id}.working.mp4"

    result_path.unlink(missing_ok=True)

    working_path.unlink(missing_ok=True)

    with SessionLocal() as session:
        job = _find_job(
            session,
            public_id,
        )

        if job is None:
            return

        if job.status == DetectionJobStatus.COMPLETED:
            return

        job.status = DetectionJobStatus.FAILED

        job.result_filename = None
        job.completed_at = utc_now()

        job.error_message = (f"{type(error).__name__}: {error}")[:2000]

        session.commit()
