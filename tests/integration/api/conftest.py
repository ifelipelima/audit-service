from uuid import uuid4

import pytest
from sqlalchemy import delete

from app.core.security import generate_api_key, hash_api_key
from app.db.session import SessionLocal
from app.models.application import Application
from app.models.audit_event import AuditEvent


@pytest.fixture
def make_application():
    """Cria aplicações de teste e remove-as, com seus eventos, ao final."""
    created_ids = []

    def factory() -> tuple[Application, str]:
        api_key = generate_api_key()
        application = Application(
            name="Test Application",
            slug=f"test-events-{uuid4().hex[:12]}",
            api_key_hash=hash_api_key(api_key),
        )
        with SessionLocal() as session:
            session.add(application)
            session.commit()
        created_ids.append(application.id)
        return application, api_key

    yield factory

    with SessionLocal() as session:
        session.execute(
            delete(AuditEvent).where(AuditEvent.application_id.in_(created_ids))
        )
        session.execute(delete(Application).where(Application.id.in_(created_ids)))
        session.commit()
