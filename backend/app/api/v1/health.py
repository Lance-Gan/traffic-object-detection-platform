import platform
from typing import Annotated

import torch
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db_session
from app.schemas.health import (
    DatabaseHealthResponse,
    HealthResponse,
    SystemHealthResponse,
)

router = APIRouter(
    prefix="/health",
    tags=["System"],
)


@router.get(
    "",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
    )


@router.get(
    "/database",
    response_model=DatabaseHealthResponse,
)
def database_health_check(
    session: Annotated[Session, Depends(get_db_session)],
) -> DatabaseHealthResponse:
    try:
        database_result = session.execute(text("SELECT DATABASE()"))
        selected_database = database_result.scalar_one()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc

    if not isinstance(selected_database, str):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not selected",
        )

    return DatabaseHealthResponse(
        status="ok",
        service=settings.app_name,
        database=selected_database,
    )


@router.get(
    "/system",
    response_model=SystemHealthResponse,
)
def system_health_check() -> SystemHealthResponse:
    return SystemHealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        python_version=platform.python_version(),
        model_name=settings.model_name,
        configured_device=(settings.inference_device),
        mps_available=(torch.backends.mps.is_available()),
        max_image_upload_bytes=(settings.max_image_upload_bytes),
    )
