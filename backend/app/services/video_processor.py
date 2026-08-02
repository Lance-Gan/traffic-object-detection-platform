import subprocess
from collections.abc import Callable
from decimal import Decimal
from math import ceil
from pathlib import Path
from time import perf_counter
from typing import Any

import cv2
import torch
from ultralytics import YOLO

from app.core.config import settings
from app.services.object_detector import (
    TARGET_CLASS_NAMES,
)
from app.services.video_types import (
    VideoDetectionData,
    VideoProcessingResult,
    VideoProgressData,
    VideoTrackSnapshot,
)

ProgressCallback = Callable[
    [VideoProgressData],
    None,
]


class VideoProcessor:
    def __init__(
        self,
        model_name: str,
        requested_device: str,
        target_fps: int,
        tracker_name: str,
        inference_size: int,
        output_max_width: int,
    ) -> None:
        self.model_name = model_name
        self.device = self._select_device(requested_device)

        self.target_fps = target_fps
        self.tracker_name = tracker_name
        self.inference_size = inference_size
        self.output_max_width = output_max_width

        self._model = YOLO(model_name)

        self._target_class_ids = self._resolve_target_class_ids()

    def process(
        self,
        input_path: Path,
        public_id: str,
        confidence_threshold: float,
        progress_callback: ProgressCallback,
    ) -> VideoProcessingResult:
        started_at = perf_counter()

        settings.video_result_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        working_path = settings.video_result_dir / f".{public_id}.working.mp4"

        final_path = settings.video_result_dir / f"{public_id}.mp4"

        working_path.unlink(missing_ok=True)

        final_path.unlink(missing_ok=True)

        capture = cv2.VideoCapture(str(input_path))

        writer: Any = None

        try:
            if not capture.isOpened():
                raise RuntimeError("The source video could not be opened")

            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

            source_fps = float(capture.get(cv2.CAP_PROP_FPS))

            source_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))

            source_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if total_frames <= 0 or source_fps <= 0 or source_width <= 0 or source_height <= 0:
                raise RuntimeError("The source video metadata is invalid")

            frame_stride = max(
                1,
                round(source_fps / self.target_fps),
            )

            output_fps = source_fps / frame_stride

            estimated_processed_frames = max(
                1,
                ceil(total_frames / frame_stride),
            )

            output_size = self._calculate_output_size(
                source_width,
                source_height,
            )

            fourcc = cv2.VideoWriter_fourcc(  # type: ignore[attr-defined]
                *"mp4v"
            )

            writer = cv2.VideoWriter(
                str(working_path),
                fourcc,
                output_fps,
                output_size,
            )

            if not writer.isOpened():
                raise RuntimeError("The temporary result video could not be created")

            source_frame_index = 0
            processed_frames = 0
            detection_count = 0
            last_reported_progress = 0

            unique_tracks: dict[
                int,
                VideoTrackSnapshot,
            ] = {}

            progress_callback(
                VideoProgressData(
                    progress_percent=5,
                    processed_frames=0,
                    detection_count=0,
                    unique_object_count=0,
                )
            )

            while True:
                success, frame = capture.read()

                if not success:
                    break

                should_process = source_frame_index % frame_stride == 0

                if not should_process:
                    source_frame_index += 1
                    continue

                resized_frame = self._resize_frame(
                    frame,
                    output_size,
                )

                results = self._model.track(
                    source=resized_frame,
                    persist=True,
                    tracker=(self.tracker_name),
                    device=self.device,
                    conf=(confidence_threshold),
                    classes=(self._target_class_ids),
                    imgsz=(self.inference_size),
                    verbose=False,
                )

                result = results[0]

                detections = self._extract_detections(
                    result=result,
                    frame_index=(source_frame_index),
                )

                detection_count += len(detections)

                self._update_unique_tracks(
                    unique_tracks,
                    detections,
                )

                annotated_frame = self._draw_detections(
                    resized_frame,
                    detections,
                )

                writer.write(annotated_frame)

                processed_frames += 1
                source_frame_index += 1

                progress_percent = min(
                    90,
                    5 + round((processed_frames / estimated_processed_frames) * 85),
                )

                should_report = (
                    progress_percent >= last_reported_progress + 2
                    or processed_frames >= estimated_processed_frames
                )

                if should_report:
                    progress_callback(
                        VideoProgressData(
                            progress_percent=(progress_percent),
                            processed_frames=(processed_frames),
                            detection_count=(detection_count),
                            unique_object_count=len(unique_tracks),
                        )
                    )

                    last_reported_progress = progress_percent

            if processed_frames == 0:
                raise RuntimeError("No video frames were processed")

        except Exception:
            working_path.unlink(missing_ok=True)

            final_path.unlink(missing_ok=True)

            raise

        finally:
            capture.release()

            if writer is not None:
                writer.release()

        progress_callback(
            VideoProgressData(
                progress_percent=95,
                processed_frames=(processed_frames),
                detection_count=(detection_count),
                unique_object_count=len(unique_tracks),
            )
        )

        try:
            self._transcode_with_ffmpeg(
                working_path=working_path,
                original_path=input_path,
                final_path=final_path,
            )
        except Exception:
            final_path.unlink(missing_ok=True)

            raise
        finally:
            working_path.unlink(missing_ok=True)

        duration_ms = max(
            0,
            round((perf_counter() - started_at) * 1000),
        )

        relative_result_path = final_path.relative_to(settings.result_dir).as_posix()

        return VideoProcessingResult(
            result_filename=(relative_result_path),
            processed_frames=(processed_frames),
            detection_count=(detection_count),
            duration_ms=duration_ms,
            device=self.device,
            unique_tracks=tuple(
                sorted(
                    unique_tracks.values(),
                    key=lambda item: item.track_id,
                )
            ),
        )

    def _extract_detections(
        self,
        result: Any,
        frame_index: int,
    ) -> tuple[
        VideoDetectionData,
        ...,
    ]:
        boxes = result.boxes

        if boxes is None or len(boxes) == 0:
            return ()

        class_ids = [int(value) for value in (boxes.cls.int().cpu().tolist())]

        confidences = [float(value) for value in (boxes.conf.cpu().tolist())]

        coordinates = boxes.xyxy.cpu().tolist()

        if boxes.id is None:
            track_ids: list[int | None] = [None for _ in class_ids]
        else:
            track_ids = [int(value) for value in (boxes.id.int().cpu().tolist())]

        detections: list[VideoDetectionData] = []

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

            detections.append(
                VideoDetectionData(
                    frame_index=(frame_index),
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

        return tuple(detections)

    @staticmethod
    def _update_unique_tracks(
        unique_tracks: dict[
            int,
            VideoTrackSnapshot,
        ],
        detections: tuple[
            VideoDetectionData,
            ...,
        ],
    ) -> None:
        for detection in detections:
            if detection.track_id is None:
                continue

            existing = unique_tracks.get(detection.track_id)

            should_replace = existing is None or detection.confidence > float(existing.confidence)

            if not should_replace:
                continue

            unique_tracks[detection.track_id] = VideoTrackSnapshot(
                frame_index=(detection.frame_index),
                track_id=(detection.track_id),
                class_id=(detection.class_id),
                class_name=(detection.class_name),
                confidence=Decimal(f"{detection.confidence:.5f}"),
                x1=detection.x1,
                y1=detection.y1,
                x2=detection.x2,
                y2=detection.y2,
            )

    @staticmethod
    def _draw_detections(
        frame: Any,
        detections: tuple[
            VideoDetectionData,
            ...,
        ],
    ) -> Any:
        frame_height = int(frame.shape[0])

        frame_width = int(frame.shape[1])

        for detection in detections:
            x1 = max(
                0,
                min(
                    frame_width - 1,
                    round(detection.x1),
                ),
            )

            y1 = max(
                0,
                min(
                    frame_height - 1,
                    round(detection.y1),
                ),
            )

            x2 = max(
                x1,
                min(
                    frame_width - 1,
                    round(detection.x2),
                ),
            )

            y2 = max(
                y1,
                min(
                    frame_height - 1,
                    round(detection.y2),
                ),
            )

            colour = (
                50 + (detection.class_id * 67) % 180,
                50 + (detection.class_id * 97) % 180,
                50 + (detection.class_id * 37) % 180,
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                colour,
                2,
            )

            track_label = f" #{detection.track_id}" if detection.track_id is not None else ""

            label = f"{detection.class_name}{track_label} {detection.confidence:.0%}"

            (
                (
                    text_width,
                    text_height,
                ),
                baseline,
            ) = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                2,
            )

            label_top = max(
                0,
                y1 - text_height - baseline - 8,
            )

            cv2.rectangle(
                frame,
                (
                    x1,
                    label_top,
                ),
                (
                    min(
                        frame_width - 1,
                        x1 + text_width + 10,
                    ),
                    y1,
                ),
                colour,
                -1,
            )

            cv2.putText(
                frame,
                label,
                (
                    x1 + 5,
                    max(
                        text_height + 2,
                        y1 - 5,
                    ),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        return frame

    def _calculate_output_size(
        self,
        source_width: int,
        source_height: int,
    ) -> tuple[int, int]:
        scale = min(
            1.0,
            self.output_max_width / source_width,
        )

        output_width = max(
            2,
            round(source_width * scale),
        )

        output_height = max(
            2,
            round(source_height * scale),
        )

        output_width -= output_width % 2

        output_height -= output_height % 2

        return (
            output_width,
            output_height,
        )

    @staticmethod
    def _resize_frame(
        frame: Any,
        output_size: tuple[int, int],
    ) -> Any:
        current_size = (
            int(frame.shape[1]),
            int(frame.shape[0]),
        )

        if current_size == output_size:
            return frame

        return cv2.resize(
            frame,
            output_size,
            interpolation=cv2.INTER_AREA,
        )

    @staticmethod
    def _transcode_with_ffmpeg(
        working_path: Path,
        original_path: Path,
        final_path: Path,
    ) -> None:
        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(working_path),
            "-i",
            str(original_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a?",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(final_path),
        ]

        completed_process = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )

        if completed_process.returncode != 0:
            error_message = completed_process.stderr.strip()

            raise RuntimeError(
                f"FFmpeg could not create the final result video: {error_message[:1000]}"
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
            raise RuntimeError("No supported traffic classes were found in the model")

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
