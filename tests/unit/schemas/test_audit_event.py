import pytest
from pydantic import ValidationError

from app.schemas.audit_event import AuditEventCreate


@pytest.fixture
def payload():
    return {
        "event_id": "evt-001",
        "actor_id": "user-25",
        "action": "occupation.ended",
        "resource_type": "occupation",
        "resource_id": "occ-90",
        "occurred_at": "2026-11-20T14:00:00Z",
        "details": {"terrain_id": "terrain-12"},
    }


def test_valid_event(payload):
    event = AuditEventCreate(**payload)

    assert event.event_id == "evt-001"
    assert event.occurred_at.tzinfo is not None
    assert event.details == {"terrain_id": "terrain-12"}


def test_optional_fields_can_be_omitted(payload):
    for field in ("actor_id", "resource_id", "details"):
        payload.pop(field)

    event = AuditEventCreate(**payload)

    assert event.actor_id is None
    assert event.resource_id is None
    assert event.details is None


@pytest.mark.parametrize("field", ["event_id", "action", "resource_type", "occurred_at"])
def test_required_fields(payload, field):
    payload.pop(field)

    with pytest.raises(ValidationError):
        AuditEventCreate(**payload)


def test_occurred_at_requires_timezone(payload):
    payload["occurred_at"] = "2026-11-20T14:00:00"

    with pytest.raises(ValidationError):
        AuditEventCreate(**payload)


def test_application_id_is_not_accepted_in_body(payload):
    payload["application_id"] = "8f38d369-8966-45e3-92ce-c9d13292f951"

    with pytest.raises(ValidationError):
        AuditEventCreate(**payload)


def test_event_id_max_length(payload):
    payload["event_id"] = "a" * 121

    with pytest.raises(ValidationError):
        AuditEventCreate(**payload)
