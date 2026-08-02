from fastapi import APIRouter

from app.api.v1 import (
    camera,
    detections,
    health,
    jobs,
    statistics,
)

api_router = APIRouter()

api_router.include_router(health.router)

api_router.include_router(detections.router)

api_router.include_router(jobs.router)

api_router.include_router(statistics.router)

api_router.include_router(camera.router)
