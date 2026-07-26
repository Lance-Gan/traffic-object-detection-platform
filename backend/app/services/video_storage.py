from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

import cv2
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import (
    EmptyFileError,
    InvalidVideoError,
    UnsupportedVideoTypeError,
    VideoTooLargeError,
    VideoTooLongError,
)

CHUNK_SIZE_BYTES = 4 * 1024 * 1024

ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}

VIDEO_EXTENSIONS = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
}


class VideoMetadata(TypedDict):
    frame_count: int
    fps: float
    width: int
    height: int
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class StoredVideo:
    original_filename: str
    stored_filename: str
    path: Path

    mime_type: str
    size_bytes: int

    frame_count: int
    fps: float
    width: int
    height: int
    duration_seconds: float


class VideoStorageService:
    def __init__(
        self,
        upload_dir: Path,
        max_upload_bytes: int,
        max_duration_seconds: int,
    ) -> None:
        self.upload_dir = upload_dir
        self.max_upload_bytes = max_upload_bytes
        self.max_duration_seconds = max_duration_seconds

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_video(
        self,
        upload: UploadFile,
    ) -> StoredVideo:
        content_type = (upload.content_type or "").lower()

        if content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
            raise UnsupportedVideoTypeError("Only MP4, MOV, and WebM videos are supported")

        if upload.size is not None and upload.size > self.max_upload_bytes:
            raise VideoTooLargeError("The uploaded video exceeds the maximum allowed size")

        extension = VIDEO_EXTENSIONS[content_type]
        file_id = uuid4().hex

        temporary_path = self.upload_dir / f"{file_id}.upload"

        final_path = self.upload_dir / f"{file_id}{extension}"

        size_bytes = 0

        try:
            upload.file.seek(0)

            with temporary_path.open("wb") as destination:
                while True:
                    chunk = upload.file.read(CHUNK_SIZE_BYTES)

                    if not chunk:
                        break

                    size_bytes += len(chunk)

                    if size_bytes > self.max_upload_bytes:
                        raise VideoTooLargeError(
                            "The uploaded video exceeds the maximum allowed size"
                        )

                    destination.write(chunk)

            if size_bytes == 0:
                raise EmptyFileError("The uploaded file is empty")

            temporary_path.replace(final_path)

            metadata = self._inspect_video(final_path)

            return StoredVideo(
                original_filename=self._safe_filename(upload.filename),
                stored_filename=final_path.name,
                path=final_path,
                mime_type=content_type,
                size_bytes=size_bytes,
                frame_count=metadata["frame_count"],
                fps=metadata["fps"],
                width=metadata["width"],
                height=metadata["height"],
                duration_seconds=metadata["duration_seconds"],
            )

        except Exception:
            temporary_path.unlink(missing_ok=True)

            final_path.unlink(missing_ok=True)

            raise

    def _inspect_video(
        self,
        path: Path,
    ) -> VideoMetadata:
        capture = cv2.VideoCapture(str(path))

        try:
            if not capture.isOpened():
                raise InvalidVideoError("The uploaded content is not a readable video")

            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

            fps = float(capture.get(cv2.CAP_PROP_FPS))

            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))

            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            success, first_frame = capture.read()

            if (
                not success
                or first_frame is None
                or frame_count <= 0
                or fps <= 0
                or width <= 0
                or height <= 0
            ):
                raise InvalidVideoError("The uploaded video metadata is invalid")

            duration_seconds = frame_count / fps

            if duration_seconds > self.max_duration_seconds:
                raise VideoTooLongError("The uploaded video exceeds the maximum duration")

            return {
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height,
                "duration_seconds": (duration_seconds),
            }

        finally:
            capture.release()

    @staticmethod
    def delete_file(
        path: Path,
    ) -> None:
        path.unlink(missing_ok=True)

    @staticmethod
    def _safe_filename(
        filename: str | None,
    ) -> str:
        candidate = (filename or "video").replace(
            "\\",
            "/",
        )

        basename = candidate.rsplit(
            "/",
            maxsplit=1,
        )[-1].strip()

        return (basename or "video")[:255]


@lru_cache
def get_video_storage_service() -> VideoStorageService:
    return VideoStorageService(
        upload_dir=(settings.video_upload_dir),
        max_upload_bytes=(settings.max_video_upload_bytes),
        max_duration_seconds=(settings.max_video_duration_seconds),
    )
