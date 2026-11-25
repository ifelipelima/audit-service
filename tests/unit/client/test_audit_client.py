import json

import httpx
import pytest

from client.audit_client import AuditClient, AuditClientError, RetryableResponseError

EVENT = {
    "event_id": "evt-001",
    "action": "occupation.ended",
    "resource_type": "occupation",
    "occurred_at": "2026-11-20T14:00:00Z",
}
CREATED = {
    "id": "8f38d369-8966-45e3-92ce-c9d13292f951",
    "event_id": "evt-001",
    "created_at": "2026-11-20T14:00:01Z",
}


def make_client(responses, requests):
    """Cliente cujo transporte devolve, em ordem, as respostas/exceções dadas."""
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    return AuditClient(
        "http://audit.test",
        api_key="aud_test",
        max_attempts=4,
        backoff_multiplier=0,
        transport=httpx.MockTransport(handler),
    )


def test_send_event_success():
    requests = []
    client = make_client([httpx.Response(201, json=CREATED)], requests)

    assert client.send_event(EVENT) == CREATED
    assert len(requests) == 1
    assert requests[0].url.path == "/api/v1/events"
    assert requests[0].headers["X-API-Key"] == "aud_test"


@pytest.mark.parametrize("status_code", [429, 502, 503, 504])
def test_retries_transient_status_with_same_event_id(status_code):
    requests = []
    client = make_client(
        [
            httpx.Response(status_code, json={"detail": "busy"}),
            httpx.Response(status_code, json={"detail": "busy"}),
            httpx.Response(201, json=CREATED),
        ],
        requests,
    )

    assert client.send_event(EVENT) == CREATED
    assert len(requests) == 3
    assert {json.loads(r.content)["event_id"] for r in requests} == {"evt-001"}


def test_retries_network_errors():
    requests = []
    client = make_client(
        [
            httpx.ConnectError("connection refused"),
            httpx.ReadTimeout("timeout"),
            httpx.Response(200, json=CREATED),
        ],
        requests,
    )

    assert client.send_event(EVENT) == CREATED
    assert len(requests) == 3


@pytest.mark.parametrize("status_code", [401, 404, 409, 422])
def test_does_not_retry_client_errors(status_code):
    requests = []
    client = make_client([httpx.Response(status_code, json={"detail": "no"})], requests)

    with pytest.raises(AuditClientError) as exc_info:
        client.send_event(EVENT)

    assert exc_info.value.status_code == status_code
    assert not isinstance(exc_info.value, RetryableResponseError)
    assert len(requests) == 1


def test_gives_up_after_max_attempts():
    requests = []
    client = make_client([httpx.Response(503, json={"detail": "down"})] * 4, requests)

    with pytest.raises(RetryableResponseError) as exc_info:
        client.send_event(EVENT)

    assert exc_info.value.status_code == 503
    assert len(requests) == 4


def test_list_events_drops_empty_filters():
    requests = []
    client = make_client([httpx.Response(200, json={"items": []})], requests)

    client.list_events(actor_id="user-25", action=None, limit=10)

    assert dict(requests[0].url.params) == {"actor_id": "user-25", "limit": "10"}
