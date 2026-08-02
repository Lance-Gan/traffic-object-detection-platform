import asyncio
import json
from collections import Counter
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session
from starlette.websockets import (
    WebSocketState,
)

from app.core.config import settings
from app.core.exceptions import (
    InvalidCameraFrameError,
)
from app.db.session import (
    get_db_session,
)
from app.schemas.camera import (
    CameraBoundingBoxResponse,
    CameraCompletedMessage,
    CameraErrorMessage,
    CameraFrameMessage,
    CameraLoadingMessage,
    CameraObjectResponse,
    CameraPongMessage,
    CameraReadyMessage,
    CameraSessionCreateRequest,
    CameraSessionCreateResponse,
    CameraSessionMetricsResponse,
)
from app.services.camera_session import (
    CameraSessionService,
)
from app.services.camera_tracker import (
    CameraTracker,
)
from app.services.camera_types import (
    CameraFrameResultData,
    CameraSessionAccumulator,
)

router = APIRouter(
    prefix="/camera",
    tags=["Camera"],
)


class CameraStreamGate:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def try_acquire(self) -> bool:
        if self._lock.locked():
            return False

        await self._lock.acquire()
        return True

    def release(self) -> None:
        if self._lock.locked():
            self._lock.release()


camera_stream_gate = CameraStreamGate()


@router.post(
    "/sessions",
    response_model=(CameraSessionCreateResponse),
    status_code=(status.HTTP_201_CREATED),
)
def create_camera_session(
    request: CameraSessionCreateRequest,
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
) -> CameraSessionCreateResponse:
    service = CameraSessionService(session)

    job = service.create(confidence_threshold=(request.confidence_threshold))

    websocket_path = f"{settings.api_v1_prefix}/camera/sessions/{job.public_id}/stream"

    return CameraSessionCreateResponse(
        public_id=job.public_id,
        status=job.status,
        websocket_path=(websocket_path),
        target_fps=(settings.camera_target_fps),
        frame_width=(settings.camera_frame_width),
        jpeg_quality=(settings.camera_jpeg_quality),
        max_frame_bytes=(settings.camera_max_frame_bytes),
        max_session_seconds=(settings.camera_max_session_seconds),
    )


@router.websocket("/sessions/{public_id}/stream")
async def camera_stream(
    websocket: WebSocket,
    public_id: UUID,
) -> None:
    origin = websocket.headers.get("origin")

    if origin is not None and origin not in settings.cors_origins:
        await websocket.close(
            code=1008,
            reason="Origin is not allowed",
        )

        return

    acquired = await camera_stream_gate.try_acquire()

    if not acquired:
        await websocket.accept()

        await websocket.send_json(
            CameraErrorMessage(
                type="error",
                message=("Another camera session is currently using the model"),
                fatal=True,
            ).model_dump(mode="json")
        )

        await websocket.close(
            code=1013,
            reason=("Camera inference is busy"),
        )

        return

    accumulator = CameraSessionAccumulator()

    claimed = False
    finalized = False

    try:
        await websocket.accept()

        claimed_session = await asyncio.to_thread(
            CameraSessionService.claim,
            str(public_id),
        )

        if claimed_session is None:
            await websocket.send_json(
                CameraErrorMessage(
                    type="error",
                    message=("The camera session is invalid or has already been used"),
                    fatal=True,
                ).model_dump(mode="json")
            )

            await websocket.close(
                code=1008,
                reason=("Invalid camera session"),
            )

            return

        claimed = True

        await websocket.send_json(
            CameraLoadingMessage(
                type="loading_model",
                message=("The object detection model is loading"),
            ).model_dump(mode="json")
        )

        tracker = await asyncio.to_thread(
            CameraTracker,
            model_name=(settings.model_name),
            requested_device=(settings.inference_device),
            confidence_threshold=(claimed_session.confidence_threshold),
            tracker_name=(settings.camera_tracker_name),
            max_frame_pixels=(settings.camera_max_frame_pixels),
            image_size=(settings.camera_frame_width),
        )

        await asyncio.to_thread(
            CameraSessionService.update_device,
            str(public_id),
            tracker.device,
        )

        await websocket.send_json(
            CameraReadyMessage(
                type="ready",
                device=tracker.device,
                model_name=(tracker.model_name),
                target_fps=(settings.camera_target_fps),
                max_session_seconds=(settings.camera_max_session_seconds),
            ).model_dump(mode="json")
        )

        invalid_frame_count = 0
        stop_reason = "client_stop"

        while True:
            if accumulator.elapsed_ms() >= settings.camera_max_session_seconds * 1000:
                stop_reason = "session_limit"

                break

            message = await websocket.receive()

            message_type = message.get("type")

            if message_type == "websocket.disconnect":
                stop_reason = "client_disconnect"

                break

            text_message = message.get("text")

            if text_message is not None:
                try:
                    command = json.loads(text_message)
                except json.JSONDecodeError:
                    await _send_camera_error(
                        websocket,
                        message=("The control message is not valid JSON"),
                        fatal=False,
                    )

                    continue

                command_type = command.get("type")

                if command_type == "stop":
                    stop_reason = "client_stop"

                    break

                if command_type == "ping":
                    await websocket.send_json(
                        CameraPongMessage(type="pong").model_dump(mode="json")
                    )

                    continue

                await _send_camera_error(
                    websocket,
                    message=("The control command is not supported"),
                    fatal=False,
                )

                continue

            frame_bytes = message.get("bytes")

            if frame_bytes is None:
                continue

            if len(frame_bytes) > settings.camera_max_frame_bytes:
                raise (InvalidCameraFrameError("The camera frame exceeds the maximum message size"))

            try:
                frame_result = await asyncio.to_thread(
                    tracker.process_frame,
                    frame_bytes,
                    accumulator.processed_frames,
                )
            except InvalidCameraFrameError as exc:
                invalid_frame_count += 1

                fatal = invalid_frame_count >= 3

                await _send_camera_error(
                    websocket,
                    message=str(exc),
                    fatal=fatal,
                )

                if fatal:
                    raise

                continue

            invalid_frame_count = 0

            accumulator.record(frame_result)

            await websocket.send_json(
                _build_frame_message(
                    frame_result,
                    accumulator,
                ).model_dump(mode="json")
            )

        await asyncio.to_thread(
            CameraSessionService.finish,
            str(public_id),
            accumulator,
            None,
        )

        finalized = True

        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_json(
                CameraCompletedMessage(
                    type=("session_completed"),
                    public_id=public_id,
                    stop_reason=stop_reason,
                    processed_frames=(accumulator.processed_frames),
                    total_detections=(accumulator.total_detections),
                    unique_objects=len(accumulator.unique_tracks),
                    duration_ms=(accumulator.elapsed_ms()),
                ).model_dump(mode="json")
            )

            await websocket.close(
                code=1000,
                reason=("Camera session completed"),
            )

    except WebSocketDisconnect:
        pass

    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"

        if claimed and not finalized:
            await asyncio.to_thread(
                CameraSessionService.finish,
                str(public_id),
                accumulator,
                error_message,
            )

            finalized = True

        if websocket.application_state == WebSocketState.CONNECTED:
            await _send_camera_error(
                websocket,
                message=("The live camera session could not continue"),
                fatal=True,
            )

            await websocket.close(
                code=1011,
                reason=("Camera processing failed"),
            )

    finally:
        if claimed and not finalized:
            await asyncio.to_thread(
                CameraSessionService.finish,
                str(public_id),
                accumulator,
                None,
            )

        camera_stream_gate.release()


async def _send_camera_error(
    websocket: WebSocket,
    message: str,
    fatal: bool,
) -> None:
    await websocket.send_json(
        CameraErrorMessage(
            type="error",
            message=message,
            fatal=fatal,
        ).model_dump(mode="json")
    )


def _build_frame_message(
    result: CameraFrameResultData,
    accumulator: CameraSessionAccumulator,
) -> CameraFrameMessage:
    summary = dict(Counter(detected_object.class_name for detected_object in result.objects))

    server_fps = (
        round(
            1000 / result.inference_ms,
            2,
        )
        if result.inference_ms > 0
        else 0.0
    )

    objects = [
        CameraObjectResponse(
            track_id=(detected_object.track_id),
            class_id=(detected_object.class_id),
            class_name=(detected_object.class_name),
            confidence=(detected_object.confidence),
            bounding_box=(
                CameraBoundingBoxResponse(
                    x1=(detected_object.x1),
                    y1=(detected_object.y1),
                    x2=(detected_object.x2),
                    y2=(detected_object.y2),
                )
            ),
        )
        for detected_object in result.objects
    ]

    return CameraFrameMessage(
        type="frame_result",
        frame_index=(result.frame_index),
        frame_width=(result.frame_width),
        frame_height=(result.frame_height),
        inference_ms=(result.inference_ms),
        server_fps=server_fps,
        objects=objects,
        summary=summary,
        session=(
            CameraSessionMetricsResponse(
                processed_frames=(accumulator.processed_frames),
                total_detections=(accumulator.total_detections),
                unique_objects=len(accumulator.unique_tracks),
                elapsed_ms=(accumulator.elapsed_ms()),
            )
        ),
    )
