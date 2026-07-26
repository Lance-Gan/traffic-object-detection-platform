from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DetectedObjectData:
    class_id: int
    class_name: str
    confidence: Decimal
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class DetectionRunResult:
    result_filename: str
    duration_ms: int
    objects: tuple[DetectedObjectData, ...]
