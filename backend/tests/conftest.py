import os
import shutil
from collections.abc import Generator
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

BACKEND_ROOT = Path(__file__).resolve().parents[1]
TEST_DATA_ROOT = BACKEND_ROOT / ".test-data"

DEFAULT_TEST_ENVIRONMENT = {
    "APP_ENV": "test",
    "LOG_LEVEL": "WARNING",
    "SQL_ECHO": "false",
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "3307",
    "DB_NAME": "traffic_detection_test",
    "DB_USER": "traffic_test",
    "DB_PASSWORD": "traffic_test_password",
    "CELERY_BROKER_URL": "redis://127.0.0.1:6380/0",
    "CELERY_RESULT_BACKEND": "redis://127.0.0.1:6380/1",
    "MODEL_NAME": "fake-yolo.pt",
    "INFERENCE_DEVICE": "cpu",
    "UPLOAD_DIR": str(TEST_DATA_ROOT / "uploads"),
    "RESULT_DIR": str(TEST_DATA_ROOT / "results"),
    "VIDEO_UPLOAD_DIR": str(TEST_DATA_ROOT / "uploads" / "videos"),
    "VIDEO_RESULT_DIR": str(TEST_DATA_ROOT / "results" / "videos"),
    "CORS_ORIGINS": ('["http://127.0.0.1:5173","http://localhost:5173"]'),
    "ALLOWED_HOSTS": ('["127.0.0.1","localhost","testserver"]'),
}

if os.environ.get("CI", "").lower() == "true":
    for variable_name, default_value in DEFAULT_TEST_ENVIRONMENT.items():
        os.environ.setdefault(
            variable_name,
            default_value,
        )
else:
    os.environ.update(DEFAULT_TEST_ENVIRONMENT)

UPLOAD_DIR = Path(os.environ["UPLOAD_DIR"])
RESULT_DIR = Path(os.environ["RESULT_DIR"])
VIDEO_UPLOAD_DIR = Path(os.environ["VIDEO_UPLOAD_DIR"])
VIDEO_RESULT_DIR = Path(os.environ["VIDEO_RESULT_DIR"])

for directory in (
    UPLOAD_DIR,
    RESULT_DIR,
    VIDEO_UPLOAD_DIR,
    VIDEO_RESULT_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import delete  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.main import create_application  # noqa: E402
from app.models import (  # noqa: E402
    DetectionJob,
    DetectionObject,
)


@pytest.fixture(scope="session")
def client() -> Generator[TestClient]:
    application = create_application()

    with TestClient(application) as test_client:
        yield test_client


def clean_database() -> None:
    with SessionLocal() as session:
        session.execute(delete(DetectionObject))
        session.execute(delete(DetectionJob))
        session.commit()


@pytest.fixture(autouse=True)
def reset_test_state() -> Generator[None]:
    clean_database()

    for directory in (
        UPLOAD_DIR,
        RESULT_DIR,
    ):
        shutil.rmtree(
            directory,
            ignore_errors=True,
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    VIDEO_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    VIDEO_RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield

    clean_database()


@pytest.fixture
def jpeg_bytes() -> bytes:
    buffer = BytesIO()

    image = Image.new(
        mode="RGB",
        size=(64, 48),
        color=(120, 140, 160),
    )

    image.save(
        buffer,
        format="JPEG",
    )

    return buffer.getvalue()
