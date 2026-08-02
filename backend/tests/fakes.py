from decimal import Decimal
from pathlib import Path

from PIL import Image

from app.services.camera_types import (
    CameraFrameResultData,
    CameraObjectData,
)
from app.services.detection_types import (
    DetectedObjectData,
    DetectionRunResult,
)


class FakeObjectDetector:
    model_name = "fake-yolo.pt"
    device = "cpu"

    def detect_image(
        self,
        input_path: Path,
        output_path: Path,
        confidence_threshold: float,
    ) -> DetectionRunResult:
        del confidence_threshold

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with Image.open(
            input_path
        ) as image:
            image.convert(
                "RGB"
            ).save(
                output_path,
                format="JPEG",
            )

        detected_object = (
            DetectedObjectData(
                class_id=2,
                class_name="car",
                confidence=Decimal(
                    "0.90000"
                ),
                x1=5.0,
                y1=6.0,
                x2=40.0,
                y2=35.0,
            )
        )

        return DetectionRunResult(
            result_filename=(
                output_path.name
            ),
            duration_ms=12,
            objects=(
                detected_object,
            ),
        )


class FakeCameraTracker:
    model_name = "fake-yolo.pt"
    device = "cpu"

    def __init__(
        self,
        **_: object,
    ) -> None:
        pass

    def process_frame(
        self,
        frame_bytes: bytes,
        frame_index: int,
    ) -> CameraFrameResultData:
        del frame_bytes

        detected_object = (
            CameraObjectData(
                track_id=7,
                class_id=2,
                class_name="car",
                confidence=0.91,
                x1=10.0,
                y1=12.0,
                x2=100.0,
                y2=90.0,
            )
        )

        return CameraFrameResultData(
            frame_index=frame_index,
            frame_width=320,
            frame_height=240,
            inference_ms=20,
            objects=(
                detected_object,
            ),
        )