from collections import Counter
from collections.abc import Mapping

from app.core.config import settings
from app.models import DetectionJob
from app.schemas.detection import (
    BoundingBoxResponse,
    DetectionJobDetailResponse,
    DetectionJobSummaryResponse,
    DetectionObjectResponse,
)


def build_job_summary(
    job: DetectionJob,
    summary: Mapping[str, int] | None = None,
) -> DetectionJobSummaryResponse:
    resolved_summary = (
        dict(summary)
        if summary is not None
        else dict(Counter(detected_object.class_name for detected_object in job.objects))
    )

    result_url = None

    if job.result_filename is not None:
        result_url = f"{settings.result_url_prefix.rstrip('/')}/{job.result_filename}"

    return DetectionJobSummaryResponse(
        public_id=job.public_id,
        source_type=job.source_type,
        status=job.status,
        original_filename=job.original_filename,
        result_url=result_url,
        detected_object_count=(job.detected_object_count),
        duration_ms=job.duration_ms,
        summary=resolved_summary,
        created_at=job.created_at,
        completed_at=job.completed_at,
        progress_percent=(job.progress_percent),
        unique_object_count=(job.unique_object_count),
        total_frames=job.total_frames,
        processed_frames=(job.processed_frames),
    )


def build_job_detail(
    job: DetectionJob,
) -> DetectionJobDetailResponse:
    summary = build_job_summary(job)

    objects = [
        DetectionObjectResponse(
            class_id=detected_object.class_id,
            class_name=detected_object.class_name,
            confidence=float(detected_object.confidence),
            bounding_box=BoundingBoxResponse(
                x1=detected_object.x1,
                y1=detected_object.y1,
                x2=detected_object.x2,
                y2=detected_object.y2,
            ),
        )
        for detected_object in sorted(
            job.objects,
            key=lambda item: item.id or 0,
        )
    ]

    return DetectionJobDetailResponse(
        **summary.model_dump(),
        model_name=job.model_name,
        device=job.device,
        confidence_threshold=float(job.confidence_threshold),
        file_size_bytes=job.file_size_bytes,
        objects=objects,
        video_duration_ms=(job.video_duration_ms),
    )
