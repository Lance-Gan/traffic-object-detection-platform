from time import perf_counter
from typing import Any

import cv2
import numpy as np
import torch
from ultralytics import YOLO

from app.core.exceptions import (
    InvalidCameraFrameError,
)
from app.services.camera_types import (
    CameraFrameResultData,
    CameraObjectData,
)
from app.services.inference_lock import (
    MODEL_INFERENCE_LOCK,
)
from app.services.object_detector import (
    TARGET_CLASS_NAMES,
)


class CameraTracker:
    def __init__(
        self,
        model_name: str,
        requested_device: str,
        confidence_threshold: float,
        tracker_name: str,
        max_frame_pixels: int,
        image_size: int,
    ) -> None:
        self.model_name = model_name
        self.device = self._select_device(requested_device)

        self.confidence_threshold = confidence_threshold

        self.tracker_name = tracker_name
        self.max_frame_pixels = max_frame_pixels
        self.image_size = image_size

        self._model = YOLO(model_name)
        self._target_class_ids = self._resolve_target_class_ids()

    def process_frame(
        self,
        frame_bytes: bytes,
        frame_index: int,
    ) -> CameraFrameResultData:
        encoded_frame = np.frombuffer(
            frame_bytes,
            dtype=np.uint8,
        )

        frame = cv2.imdecode(
            encoded_frame,
            cv2.IMREAD_COLOR,
        )

        if frame is None:
            raise InvalidCameraFrameError("The camera frame could not be decoded")

        frame_height = int(frame.shape[0])

        frame_width = int(frame.shape[1])

        if frame_width <= 0 or frame_height <= 0:
            raise InvalidCameraFrameError("The camera frame dimensions are invalid")

        if frame_width * frame_height > self.max_frame_pixels:
            raise InvalidCameraFrameError("The camera frame exceeds the maximum pixel count")

        started_at = perf_counter()

        with MODEL_INFERENCE_LOCK:
            results = self._model.track(
                source=frame,
                persist=True,
                tracker=self.tracker_name,
                device=self.device,
                conf=self.confidence_threshold,
                classes=self._target_class_ids,
                imgsz=self.image_size,
                verbose=False,
            )

        result = results[0]

        objects: list[CameraObjectData] = []

        boxes = result.boxes

        if boxes is not None and len(boxes) > 0:
            class_ids = [int(value) for value in (boxes.cls.int().cpu().tolist())]

            confidences = [float(value) for value in (boxes.conf.cpu().tolist())]

            coordinates = boxes.xyxy.cpu().tolist()

            if boxes.id is None:
                track_ids: list[int | None] = [None for _ in class_ids]
            else:
                track_ids = [int(value) for value in (boxes.id.int().cpu().tolist())]

            for (
                track_id,
                class_id,
                confidence,
                bounding_box,
            ) in zip(
                track_ids,
                class_ids,
                confidences,
                coordinates,
                strict=True,
            ):
                class_name = str(result.names[class_id])

                x1, y1, x2, y2 = (float(value) for value in bounding_box)

                objects.append(
                    CameraObjectData(
                        track_id=track_id,
                        class_id=class_id,
                        class_name=class_name,
                        confidence=round(
                            confidence,
                            5,
                        ),
                        x1=round(
                            max(0.0, x1),
                            2,
                        ),
                        y1=round(
                            max(0.0, y1),
                            2,
                        ),
                        x2=round(
                            max(0.0, x2),
                            2,
                        ),
                        y2=round(
                            max(0.0, y2),
                            2,
                        ),
                    )
                )

        inference_ms = max(
            0,
            round((perf_counter() - started_at) * 1000),
        )

        return CameraFrameResultData(
            frame_index=frame_index,
            frame_width=frame_width,
            frame_height=frame_height,
            inference_ms=inference_ms,
            objects=tuple(objects),
        )

    def _resolve_target_class_ids(
        self,
    ) -> list[int]:
        model_names: Any = self._model.names

        if isinstance(
            model_names,
            dict,
        ):
            class_ids = [
                int(class_id)
                for (
                    class_id,
                    class_name,
                ) in model_names.items()
                if (class_name in TARGET_CLASS_NAMES)
            ]
        else:
            class_ids = [
                class_id
                for (
                    class_id,
                    class_name,
                ) in enumerate(model_names)
                if (class_name in TARGET_CLASS_NAMES)
            ]

        if not class_ids:
            raise RuntimeError("No target classes were found in the selected model")

        return class_ids

    @staticmethod
    def _select_device(
        requested_device: str,
    ) -> str:
        normalized_device = requested_device.strip().lower()

        if normalized_device != "auto":
            return normalized_device

        if torch.backends.mps.is_available():
            return "mps"

        return "cpu"
