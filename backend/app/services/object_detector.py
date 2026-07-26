from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from threading import Lock
from time import perf_counter
from typing import Any

import torch
from ultralytics import YOLO

from app.core.config import settings
from app.services.detection_types import (
    DetectedObjectData,
    DetectionRunResult,
)

TARGET_CLASS_NAMES = {
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "traffic light",
    "stop sign",
}


class ObjectDetector:
    def __init__(
        self,
        model_name: str,
        requested_device: str,
    ) -> None:
        self.model_name = model_name
        self.device = self._select_device(requested_device)
        self._model = YOLO(model_name)
        self._prediction_lock = Lock()
        self._target_class_ids = self._resolve_target_class_ids()

    def detect_image(
        self,
        input_path: Path,
        output_path: Path,
        confidence_threshold: float,
    ) -> DetectionRunResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        started_at = perf_counter()

        with self._prediction_lock:
            results = self._model.predict(
                source=str(input_path),
                device=self.device,
                conf=confidence_threshold,
                classes=self._target_class_ids,
                verbose=False,
            )

        result = results[0]
        result.save(filename=str(output_path))

        detected_objects: list[DetectedObjectData] = []

        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                class_name = str(result.names[class_id])
                confidence = float(box.conf[0].item())

                x1, y1, x2, y2 = (float(value) for value in box.xyxy[0].tolist())

                detected_objects.append(
                    DetectedObjectData(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=Decimal(f"{confidence:.5f}"),
                        x1=round(max(0.0, x1), 2),
                        y1=round(max(0.0, y1), 2),
                        x2=round(max(0.0, x2), 2),
                        y2=round(max(0.0, y2), 2),
                    )
                )

        duration_ms = max(
            0,
            int((perf_counter() - started_at) * 1000),
        )

        return DetectionRunResult(
            result_filename=output_path.name,
            duration_ms=duration_ms,
            objects=tuple(detected_objects),
        )

    def _resolve_target_class_ids(self) -> list[int]:
        model_names: Any = self._model.names

        if isinstance(model_names, dict):
            return [
                int(class_id)
                for class_id, class_name in model_names.items()
                if class_name in TARGET_CLASS_NAMES
            ]

        return [
            class_id
            for class_id, class_name in enumerate(model_names)
            if class_name in TARGET_CLASS_NAMES
        ]

    @staticmethod
    def _select_device(requested_device: str) -> str:
        normalized_device = requested_device.strip().lower()

        if normalized_device != "auto":
            return normalized_device

        if torch.backends.mps.is_available():
            return "mps"

        return "cpu"


@lru_cache
def get_object_detector() -> ObjectDetector:
    return ObjectDetector(
        model_name=settings.model_name,
        requested_device=settings.inference_device,
    )
