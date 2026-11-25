from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
URL = "/api/v1/events"


def event_payload(**overrides):
    payload = {
        "event_id": f"evt-{uuid4().hex[:8]}",
        "actor_id": "user-25",
        "action": "occupation.ended",
        "resource_type": "occupation",
        "resource_id": "occ-90",
        "occurred_at": "2026-11-20T14:00:00Z",
        "details": {"terrain_id": "terrain-12"},
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "aud_invalid_key"}])
def test_create_event_requires_valid_api_key(headers):
    response = client.post(URL, json=event_payload(), headers=headers)
    assert response.status_code == 401


def test_create_event(make_application):
    _, api_key = make_application()
    payload = event_payload()

    response = client.post(URL, json=payload, headers={"X-API-Key": api_key})

    assert response.status_code == 201
    data = response.json()
    assert data["event_id"] == payload["event_id"]
    assert set(data) == {"id", "event_id", "created_at"}


def test_create_event_with_invalid_data(make_application):
    _, api_key = make_application()
    payload = event_payload(occurred_at="2026-11-20T14:00:00")

    response = client.post(URL, json=payload, headers={"X-API-Key": api_key})

    assert response.status_code == 422


def test_resend_identical_event_is_idempotent(make_application):
    _, api_key = make_application()
    payload = event_payload()
    headers = {"X-API-Key": api_key}

    first = client.post(URL, json=payload, headers=headers)
    second = client.post(URL, json=payload, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]


def test_reuse_event_id_with_different_content(make_application):
    _, api_key = make_application()
    payload = event_payload()
    headers = {"X-API-Key": api_key}

    client.post(URL, json=payload, headers=headers)
    response = client.post(
        URL, json={**payload, "action": "occupation.started"}, headers=headers
    )

    assert response.status_code == 409


def test_same_event_id_in_different_applications(make_application):
    _, key_a = make_application()
    _, key_b = make_application()
    payload = event_payload()

    response_a = client.post(URL, json=payload, headers={"X-API-Key": key_a})
    response_b = client.post(URL, json=payload, headers={"X-API-Key": key_b})

    assert response_a.status_code == 201
    assert response_b.status_code == 201
    assert response_a.json()["id"] != response_b.json()["id"]


def test_get_event_by_id(make_application):
    _, api_key = make_application()
    headers = {"X-API-Key": api_key}
    payload = event_payload()
    created = client.post(URL, json=payload, headers=headers).json()

    response = client.get(f"{URL}/{created['id']}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == payload["event_id"]
    assert data["details"] == payload["details"]


def test_get_event_from_other_application_returns_404(make_application):
    _, key_a = make_application()
    _, key_b = make_application()
    created = client.post(
        URL, json=event_payload(), headers={"X-API-Key": key_a}
    ).json()

    response = client.get(f"{URL}/{created['id']}", headers={"X-API-Key": key_b})

    assert response.status_code == 404


def test_get_missing_event(make_application):
    _, api_key = make_application()

    response = client.get(f"{URL}/{uuid4()}", headers={"X-API-Key": api_key})

    assert response.status_code == 404
