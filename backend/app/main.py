from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)


def create_application() -> FastAPI:
    configure_logging(
        settings.log_level,
    )

    settings.upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.result_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.video_upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.video_result_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    application = FastAPI(
        title=settings.app_name,
        description=(
            "API for traffic object detection and analytics"
        ),
        version=settings.app_version,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=(
            settings.cors_origins
        ),
        allow_credentials=False,
        allow_methods=[
            "GET",
            "POST",
            "OPTIONS",
        ],
        allow_headers=["*"],
    )

    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=(
            settings.allowed_hosts
        ),
    )

    application.add_middleware(
        RequestSizeLimitMiddleware,
        max_body_bytes=(
            settings.max_request_body_bytes
        ),
    )

    application.add_middleware(
        SecurityHeadersMiddleware,
    )

    application.add_middleware(
        RequestContextMiddleware,
    )

    application.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    application.mount(
        settings.result_url_prefix,
        StaticFiles(
            directory=settings.result_dir,
        ),
        name="detection-results",
    )

    return application


app = create_application()