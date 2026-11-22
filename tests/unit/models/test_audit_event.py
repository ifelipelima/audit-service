import pytest
from sqlalchemy import UniqueConstraint

from app.db.base import Base
from app.models import Application, AuditEvent


def test_application_model_is_registered():
    assert Application.__table__.name in Base.metadata.tables

@pytest.mark.parametrize(
    "field",
    [
        "event_id",
        "application_id",
        "action",
        "resource_type",
        "occurred_at",
    ]
)
def test_audit_event_required_fields(field):
    columns = AuditEvent.__table__.columns[field]
    assert columns.nullable is False

@pytest.mark.parametrize(
    "field",
    [
        "actor_id",
        "resource_id",
        "details",
    ]
)
def test_audit_optional_fields(field):
    columns = AuditEvent.__table__.columns[field]
    assert columns.nullable is True

def test_audit_event_unique_constraint():
    constraints = AuditEvent.__table__.constraints
    assert any(isinstance(constraint, UniqueConstraint) and set(constraint.columns.keys()) == {"application_id", "event_id"} for constraint in constraints)

def test_audit_event_query_index():
    indexes = AuditEvent.__table__.indexes
    assert any(set(index.columns.keys()) == {"application_id", "occurred_at"} for index in indexes)

def test_application_relationship():
    assert "events" in Application.__mapper__.relationships
    assert "application" in AuditEvent.__mapper__.relationships