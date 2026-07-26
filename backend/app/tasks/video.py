from app.db.session import SessionLocal
from app.models import (
    DetectionJobStatus,
)
from app.repositories.detection_repository import (
    DetectionRepository,
)
from app.worker.celery_app import (
    celery_app,
)


@celery_app.task(  # type: ignore[untyped-decorator]
    bind=True,
    name="app.tasks.video.process_video_job",
)
def process_video_job(
    self: object,
    public_id: str,
) -> None:
    with SessionLocal() as session:
        repository = DetectionRepository(session)

        job = repository.get_by_public_id(public_id)

        if job is None:
            return

        if job.status == DetectionJobStatus.COMPLETED:
            return

        try:
            job.status = DetectionJobStatus.PROCESSING

            job.device = "worker"
            job.progress_percent = 10

            session.commit()

            # The real YOLO tracking loop is added in the next step.
            job.progress_percent = 100

            job.status = DetectionJobStatus.COMPLETED

            session.commit()

        except Exception as exc:
            session.rollback()

            failed_job = repository.get_by_public_id(public_id)

            if failed_job is not None:
                failed_job.status = DetectionJobStatus.FAILED

                failed_job.error_message = (f"{type(exc).__name__}: {exc}")[:2000]

                session.commit()

            raise
