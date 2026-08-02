from fastapi.testclient import (
    TestClient,
)
import pytest

from app.api.v1 import camera
from tests.fakes import (
    FakeCameraTracker,
)


@pytest.mark.integration
@pytest.mark.websocket
def test_camera_websocket_session(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        camera,
        "CameraTracker",
        FakeCameraTracker,
    )

    create_response = client.post(
        "/api/v1/camera/sessions",
        json={
            "confidence_threshold": 0.25,
        },
    )

    assert (
        create_response.status_code
        == 201
    )

    session_data = (
        create_response.json()
    )

    websocket_path = (
        session_data["websocket_path"]
    )

    with client.websocket_connect(
        websocket_path,
        headers={
            "origin": (
                "http://127.0.0.1:5173"
            )
        },
    ) as websocket:
        loading_message = (
            websocket.receive_json()
        )

        assert (
            loading_message["type"]
            == "loading_model"
        )

        ready_message = (
            websocket.receive_json()
        )

        assert (
            ready_message["type"]
            == "ready"
        )

        assert (
            ready_message["device"]
            == "cpu"
        )

        websocket.send_text(
            '{"type":"ping"}'
        )

        pong_message = (
            websocket.receive_json()
        )

        assert (
            pong_message["type"]
            == "pong"
        )

        websocket.send_bytes(
            b"fake-frame"
        )

        frame_message = (
            websocket.receive_json()
        )

        assert (
            frame_message["type"]
            == "frame_result"
        )

        assert (
            frame_message["summary"]
            == {"car": 1}
        )

        assert (
            frame_message["objects"][0][
                "track_id"
            ]
            == 7
        )

        websocket.send_text(
            '{"type":"stop"}'
        )

        completed_message = (
            websocket.receive_json()
        )

        assert (
            completed_message["type"]
            == "session_completed"
        )

        assert (
            completed_message[
                "unique_objects"
            ]
            == 1
        )

    public_id = (
        session_data["public_id"]
    )

    job_response = client.get(
        f"/api/v1/jobs/{public_id}"
    )

    assert job_response.status_code == 200

    assert (
        job_response.json()["status"]
        == "completed"
    )