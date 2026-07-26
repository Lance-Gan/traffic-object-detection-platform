from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.detection_repository import (
    DetectionRepository,
)
from app.schemas.detection import (
    DetectionJobDetailResponse,
    DetectionJobListResponse,
)
from app.schemas.job import DetectionJobListQuery
from app.services.job_presenter import (
    build_job_detail,
    build_job_summary,
)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get(
    "",
    response_model=DetectionJobListResponse,
)
def list_jobs(
    filters: Annotated[
        DetectionJobListQuery,
        Query(),
    ],
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
) -> DetectionJobListResponse:
    repository = DetectionRepository(session)
    page_data = repository.list_jobs(filters)

    total_pages = ceil(page_data.total / filters.page_size) if page_data.total > 0 else 0

    items = [
        build_job_summary(
            job,
            page_data.summaries.get(
                job.id,
                {},
            ),
        )
        for job in page_data.jobs
    ]

    return DetectionJobListResponse(
        items=items,
        page=filters.page,
        page_size=filters.page_size,
        count=len(items),
        total=page_data.total,
        total_pages=total_pages,
        has_previous=filters.page > 1,
        has_next=(total_pages > 0 and filters.page < total_pages),
    )


@router.get(
    "/{public_id}",
    response_model=DetectionJobDetailResponse,
)
def get_job(
    public_id: UUID,
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
) -> DetectionJobDetailResponse:
    repository = DetectionRepository(session)

    job = repository.get_by_public_id(str(public_id))

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection job was not found",
        )

    return build_job_detail(job)
