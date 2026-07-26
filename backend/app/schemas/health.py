from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class DatabaseHealthResponse(HealthResponse):
    database: str


class SystemHealthResponse(HealthResponse):
    version: str
    environment: str

    python_version: str

    model_name: str
    configured_device: str
    mps_available: bool

    max_image_upload_bytes: int
