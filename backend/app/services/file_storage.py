import warnings
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.exceptions import (
    EmptyFileError,
    ImageTooLargeError,
    InvalidImageError,
    UnsupportedImageTypeError,
)

CHUNK_SIZE_BYTES = 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


@dataclass(frozen=True, slots=True)
class StoredImage:
    original_filename: str
    stored_filename: str
    path: Path
    mime_type: str
    size_bytes: int


class FileStorageService:
    def __init__(
        self,
        upload_dir: Path,
        max_upload_bytes: int,
    ) -> None:
        self.upload_dir = upload_dir
        self.max_upload_bytes = max_upload_bytes
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_image(self, upload: UploadFile) -> StoredImage:
        content_type = (upload.content_type or "").lower()

        if content_type not in ALLOWED_CONTENT_TYPES:
            raise UnsupportedImageTypeError("Only JPEG, PNG, and WebP images are supported")

        if upload.size is not None and upload.size > self.max_upload_bytes:
            raise ImageTooLargeError("The uploaded image exceeds the maximum allowed size")

        original_filename = self._safe_original_filename(upload.filename)
        file_id = uuid4().hex
        temporary_path = self.upload_dir / f"{file_id}.upload"

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
                        raise ImageTooLargeError(
                            "The uploaded image exceeds the maximum allowed size"
                        )

                    destination.write(chunk)

            if size_bytes == 0:
                raise EmptyFileError("The uploaded file is empty")

            image_format = self._verify_image(temporary_path)
            extension = FORMAT_EXTENSIONS.get(image_format)

            if extension is None:
                raise UnsupportedImageTypeError("The decoded image format is not supported")

            stored_filename = f"{file_id}{extension}"
            final_path = self.upload_dir / stored_filename
            temporary_path.replace(final_path)

            return StoredImage(
                original_filename=original_filename,
                stored_filename=stored_filename,
                path=final_path,
                mime_type=content_type,
                size_bytes=size_bytes,
            )
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def delete_file(path: Path) -> None:
        path.unlink(missing_ok=True)

    @staticmethod
    def _safe_original_filename(filename: str | None) -> str:
        candidate = (filename or "upload").replace("\\", "/")
        basename = candidate.rsplit("/", maxsplit=1)[-1].strip()
        return (basename or "upload")[:255]

    @staticmethod
    def _verify_image(path: Path) -> str:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter(
                    "error",
                    Image.DecompressionBombWarning,
                )

                with Image.open(path) as image:
                    image_format = image.format
                    image.verify()

                with Image.open(path) as image:
                    image.load()

            if image_format is None:
                raise InvalidImageError("The uploaded file has no recognizable image format")

            return image_format
        except (
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            UnidentifiedImageError,
            OSError,
        ) as exc:
            raise InvalidImageError("The uploaded content is not a safe and valid image") from exc


@lru_cache
def get_file_storage_service() -> FileStorageService:
    return FileStorageService(
        upload_dir=settings.upload_dir,
        max_upload_bytes=settings.max_image_upload_bytes,
    )
