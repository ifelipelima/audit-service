from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
URL = "/api/v1/events"


def register(api_key, **fields):
    payload = {
        "event_id": f"evt-{uuid4().hex[:8]}",
        "action": "occupation.ended",
        "resource_type": "occupation",
        "occurred_at": "2026-11-20T14:00:00Z",
    }
    payload.update(fields)
    response = client.post(URL, json=payload, headers={"X-API-Key": api_key})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def populated(make_application):
    _, api_key = make_application()
    register(api_key, actor_id="user-1", occurred_at="2026-11-18T10:00:00Z")
    register(api_key, actor_id="user-2", occurred_at="2026-11-19T10:00:00Z")
    register(
        api_key,
        actor_id="user-1",
        action="terrain.created",
        resource_type="terrain",
        resource_id="terrain-12",
        occurred_at="2026-11-20T10:00:00Z",
    )
    return api_key


def query(api_key, **params):
    response = client.get(URL, params=params, headers={"X-API-Key": api_key})
    assert response.status_code == 200, response.text
    return response.json()


def test_list_requires_api_key():
    assert client.get(URL).status_code == 401


def test_list_orders_most_recent_first(populated):
    page = query(populated)

    dates = [item["occurred_at"] for item in page["items"]]
    assert len(dates) == 3
    assert dates == sorted(dates, reverse=True)
    assert page["limit"] == 20
    assert page["offset"] == 0


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ({"actor_id": "user-1"}, 2),
        ({"action": "terrain.created"}, 1),
        ({"resource_type": "occupation"}, 2),
        ({"resource_id": "terrain-12"}, 1),
        ({"actor_id": "user-1", "resource_type": "occupation"}, 1),
        ({"actor_id": "nobody"}, 0),
    ],
)
def test_list_filters(populated, params, expected):
    assert len(query(populated, **params)["items"]) == expected


def test_list_filters_by_period(populated):
    page = query(
        populated,
        occurred_from="2026-11-19T00:00:00Z",
        occurred_to="2026-11-19T23:59:59Z",
    )

    assert [item["actor_id"] for item in page["items"]] == ["user-2"]


def test_list_rejects_inverted_period(populated):
    response = client.get(
        URL,
        params={
            "occurred_from": "2026-11-20T00:00:00Z",
            "occurred_to": "2026-11-19T00:00:00Z",
        },
        headers={"X-API-Key": populated},
    )
    assert response.status_code == 422


def test_list_pagination(populated):
    first = query(populated, limit=2, offset=0)["items"]
    second = query(populated, limit=2, offset=2)["items"]

    assert len(first) == 2
    assert len(second) == 1
    assert {e["id"] for e in first}.isdisjoint({e["id"] for e in second})


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_list_rejects_invalid_pagination(populated, params):
    response = client.get(URL, params=params, headers={"X-API-Key": populated})
    assert response.status_code == 422


def test_list_only_returns_own_events(populated, make_application):
    _, other_key = make_application()
    register(other_key)

    assert len(query(other_key)["items"]) == 1
    assert len(query(populated)["items"]) == 3
