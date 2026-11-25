from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.repositories.audit_event import AuditEventRepository
from app.schemas.audit_event import AuditEventCreate
from app.services.audit_event import (
    AuditEventConflictError,
    AuditEventNotFoundError,
    AuditEventService,
)

APPLICATION_ID = uuid4()


@pytest.fixture
def session():
    return Mock(spec=Session)


@pytest.fixture
def repository():
    return Mock(spec=AuditEventRepository)


@pytest.fixture
def service(session, repository):
    instance = AuditEventService(session)
    instance.repository = repository
    return instance


@pytest.fixture
def data():
    return AuditEventCreate(
        event_id="evt-001",
        actor_id="user-25",
        action="occupation.ended",
        resource_type="occupation",
        resource_id="occ-90",
        occurred_at=datetime(2026, 11, 20, 14, tzinfo=UTC),
        details={"terrain_id": "terrain-12"},
    )


def stored_from(data, **overrides):
    fields = data.model_dump()
    fields.update(overrides)
    return AuditEvent(application_id=APPLICATION_ID, **fields)


def integrity_error():
    return IntegrityError(statement="INSERT", params={}, orig=Exception("duplicate key"))


def test_register_new_event(service, session, repository, data):
    repository.get_by_event_id.return_value = None
    repository.create.side_effect = lambda app_id, d: stored_from(d)

    event, created = service.register(APPLICATION_ID, data)

    assert created is True
    assert event.event_id == "evt-001"
    repository.create.assert_called_once_with(APPLICATION_ID, data)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(event)


def test_register_identical_event_returns_existing(service, session, repository, data):
    existing = stored_from(data)
    repository.get_by_event_id.return_value = existing

    event, created = service.register(APPLICATION_ID, data)

    assert created is False
    assert event is existing
    repository.create.assert_not_called()
    session.commit.assert_not_called()


def test_register_same_event_id_with_different_content(service, session, repository, data):
    repository.get_by_event_id.return_value = stored_from(data, action="other.action")

    with pytest.raises(AuditEventConflictError):
        service.register(APPLICATION_ID, data)

    repository.create.assert_not_called()


def test_register_concurrent_identical_event(service, session, repository, data):
    existing = stored_from(data)
    repository.get_by_event_id.side_effect = [None, existing]
    session.commit.side_effect = integrity_error()

    event, created = service.register(APPLICATION_ID, data)

    assert created is False
    assert event is existing
    session.rollback.assert_called_once()
    session.refresh.assert_not_called()


def test_register_concurrent_conflicting_event(service, session, repository, data):
    repository.get_by_event_id.side_effect = [None, stored_from(data, details=None)]
    session.commit.side_effect = integrity_error()

    with pytest.raises(AuditEventConflictError):
        service.register(APPLICATION_ID, data)

    session.rollback.assert_called_once()


def test_register_other_integrity_error(service, session, repository, data):
    repository.get_by_event_id.side_effect = [None, None]
    session.commit.side_effect = integrity_error()

    with pytest.raises(IntegrityError):
        service.register(APPLICATION_ID, data)


def test_get_event(service, repository, data):
    existing = stored_from(data)
    repository.get_by_id.return_value = existing

    assert service.get(APPLICATION_ID, uuid4()) is existing


def test_get_missing_event(service, repository):
    repository.get_by_id.return_value = None

    with pytest.raises(AuditEventNotFoundError):
        service.get(APPLICATION_ID, uuid4())
