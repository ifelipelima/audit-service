from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.repositories.audit_event import AuditEventRepository
from app.schemas.audit_event import AuditEventCreate


def make_data(**overrides):
    data = {
        "event_id": "evt-001",
        "action": "occupation.ended",
        "resource_type": "occupation",
        "occurred_at": datetime(2026, 11, 20, 14, tzinfo=UTC),
    }
    data.update(overrides)
    return AuditEventCreate(**data)


def test_create_event():
    session = Mock(spec=Session)
    repository = AuditEventRepository(session)
    application_id = uuid4()

    event = repository.create(application_id, make_data(details={"a": 1}))

    assert isinstance(event, AuditEvent)
    assert event.application_id == application_id
    assert event.event_id == "evt-001"
    assert event.details == {"a": 1}
    session.add.assert_called_once_with(event)
    session.commit.assert_not_called()


def test_get_by_event_id_filters_by_application():
    session = Mock(spec=Session)
    application_id = uuid4()

    AuditEventRepository(session).get_by_event_id(application_id, "evt-001")

    params = session.scalar.call_args.args[0].compile().params.values()
    assert application_id in params
    assert "evt-001" in params


def test_get_by_id_filters_by_application():
    session = Mock(spec=Session)
    application_id = uuid4()
    event_uuid = uuid4()

    AuditEventRepository(session).get_by_id(application_id, event_uuid)

    params = session.scalar.call_args.args[0].compile().params.values()
    assert application_id in params
    assert event_uuid in params
