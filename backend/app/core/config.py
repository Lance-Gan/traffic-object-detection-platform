from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "Traffic Object Detection API"
    app_version: str = "0.2.0"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    sql_echo: bool = False

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: SecretStr

    model_name: str = "yolo26n.pt"
    inference_device: str = "auto"
    default_confidence_threshold: Decimal = Decimal("0.2500")

    max_image_upload_bytes: int = 25 * 1024 * 1024
    upload_dir: Path = BACKEND_ROOT / "uploads"
    result_dir: Path = BACKEND_ROOT / "results"
    result_url_prefix: str = "/media/results"

    celery_broker_url: str
    celery_result_backend: str

    max_video_upload_bytes: int = 250 * 1024 * 1024
    max_video_duration_seconds: int = 120
    video_target_fps: int = 10

    video_tracker_name: str = "bytetrack.yaml"
    video_inference_size: int = 640
    video_output_max_width: int = 1280

    camera_target_fps: int = 5
    camera_frame_width: int = 640
    camera_jpeg_quality: float = 0.72

    camera_max_frame_bytes: int = 2 * 1024 * 1024
    camera_max_frame_pixels: int = 1280 * 720
    camera_max_session_seconds: int = 10 * 60

    camera_tracker_name: str = "bytetrack.yaml"

    log_level: str = "INFO"

    allowed_hosts: list[str] = [
        "127.0.0.1",
        "localhost",
        "testserver",
    ]

    max_request_body_bytes: int = 270 * 1024 * 1024

    video_upload_dir: Path = BACKEND_ROOT / "uploads" / "videos"

    video_result_dir: Path = BACKEND_ROOT / "results" / "videos"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def build_database_url(self) -> URL:
        return URL.create(
            drivername="mysql+pymysql",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
