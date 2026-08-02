from io import BytesIO

import pytest
from fastapi import UploadFile

from app.core.exceptions import (
    ImageTooLargeError,
)
from app.services.file_storage import (
    FileStorageService,
)


def test_rejects_image_above_limit(
    tmp_path,
) -> None:
    service = FileStorageService(
        upload_dir=tmp_path,
        max_upload_bytes=4,
    )

    upload = UploadFile(
        filename="large.jpg",
        file=BytesIO(
            b"12345"
        ),
        headers={
            "content-type": (
                "image/jpeg"
            )
        },
    )

    with pytest.raises(
        ImageTooLargeError
    ):
        service.save_image(upload)