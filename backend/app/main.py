from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings


def create_application() -> FastAPI:
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
        description=("API for traffic object detection and analytics"),
        version=settings.app_version,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=[
            "GET",
            "POST",
            "OPTIONS",
        ],
        allow_headers=["*"],
    )

    application.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    application.mount(
        settings.result_url_prefix,
        StaticFiles(directory=settings.result_dir),
        name="detection-results",
    )

    return application


app = create_application()
