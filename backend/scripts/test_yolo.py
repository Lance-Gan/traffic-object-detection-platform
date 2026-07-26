from pathlib import Path

import torch
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "samples" / "bus.jpg"
OUTPUT_PATH = PROJECT_ROOT / "samples" / "bus_result.jpg"


def select_device() -> str:
    """Use MPS on Apple Silicon when available; otherwise, use CPU."""
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Test image not found: {INPUT_PATH}")

    device = select_device()

    print(f"Using device: {device}")
    print("Loading the YOLO26n model...")

    model = YOLO("yolo26n.pt")

    results = model.predict(
        source=str(INPUT_PATH),
        device=device,
        conf=0.25,
        verbose=False,
    )

    result = results[0]
    result.save(filename=str(OUTPUT_PATH))

    print(f"Detection complete: {OUTPUT_PATH}")

    if result.boxes is None:
        print("No objects detected")
        return

    for box in result.boxes:
        class_id = int(box.cls.item())
        confidence = float(box.conf.item())
        class_name = result.names[class_id]

        print(f"Class={class_name}, Confidence={confidence:.2%}")


if __name__ == "__main__":
    main()
