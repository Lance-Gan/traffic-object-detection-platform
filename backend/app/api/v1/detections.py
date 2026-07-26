from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    DetectionProcessingError,
    EmptyFileError,
    ImageTooLargeError,
    InvalidImageError,
    InvalidVideoError,
    UnsupportedImageTypeError,
    UnsupportedVideoTypeError,
    VideoTooLargeError,
    VideoTooLongError,
)
from app.db.session import get_db_session
from app.repositories.detection_repository import (
    DetectionRepository,
)
from app.schemas.detection import (
    DetectionJobDetailResponse,
)
from app.services.image_detection import (
    create_image_detection_service,
)
from app.services.job_presenter import build_job_detail
from app.services.video_detection import (
    create_video_detection_service,
)

router = APIRouter(
    prefix="/detections",
    tags=["Detections"],
)


@router.post(
    "/images",
    response_model=DetectionJobDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def detect_image(
    file: Annotated[
        UploadFile,
        File(description="JPEG, PNG, or WebP image"),
    ],
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
    confidence_threshold: Annotated[
        float,
        Form(ge=0.01, le=1.0),
    ] = float(settings.default_confidence_threshold),
) -> DetectionJobDetailResponse:
    try:
        service = create_image_detection_service(session)

        job = service.process(
            upload=file,
            confidence_threshold=confidence_threshold,
        )

        return build_job_detail(job)
    except UnsupportedImageTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc
    except ImageTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except (InvalidImageError, EmptyFileError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DetectionProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image detection failed",
        ) from exc
    finally:
        file.file.close()


@router.post(
    "/videos",
    response_model=DetectionJobDetailResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def detect_video(
    file: Annotated[
        UploadFile,
        File(description=("MP4, MOV, or WebM video")),
    ],
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
    confidence_threshold: Annotated[
        float,
        Form(ge=0.01, le=1.0),
    ] = float(settings.default_confidence_threshold),
) -> DetectionJobDetailResponse:
    try:
        service = create_video_detection_service(session)

        job = service.create_job(
            upload=file,
            confidence_threshold=(confidence_threshold),
        )

        loaded_job = DetectionRepository(session).get_by_public_id(job.public_id)

        if loaded_job is None:
            raise HTTPException(
                status_code=500,
                detail=("The video job could not be loaded"),
            )

        return build_job_detail(loaded_job)

    except UnsupportedVideoTypeError as exc:
        raise HTTPException(
            status_code=(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE),
            detail=str(exc),
        ) from exc

    except VideoTooLargeError as exc:
        raise HTTPException(
            status_code=413,
            detail=str(exc),
        ) from exc

    except (
        InvalidVideoError,
        VideoTooLongError,
        EmptyFileError,
    ) as exc:
        raise HTTPException(
            status_code=(status.HTTP_400_BAD_REQUEST),
            detail=str(exc),
        ) from exc

    finally:
        file.file.close()
