from fastapi.testclient import (
    TestClient,
)


def test_system_health(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/health/system"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["python_version"].startswith(
        "3.13"
    )


def test_database_health(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/health/database"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["database"] == (
        "traffic_detection_test"
    )

def test_security_headers(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/health/system"
    )

    assert (
        response.headers[
            "x-content-type-options"
        ]
        == "nosniff"
    )

    assert (
        response.headers[
            "x-frame-options"
        ]
        == "DENY"
    )

    assert (
        response.headers[
            "referrer-policy"
        ]
        == "no-referrer"
    )

    assert (
        response.headers[
            "x-request-id"
        ]
    )


def test_preserves_valid_request_id(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/health/system",
        headers={
            "X-Request-ID": (
                "test-request-123"
            )
        },
    )

    assert (
        response.headers[
            "x-request-id"
        ]
        == "test-request-123"
    )