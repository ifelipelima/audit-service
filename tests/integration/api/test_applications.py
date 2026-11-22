from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.security import hash_api_key
from app.db.session import SessionLocal
from app.main import app
from app.models import Application


def test_create_application_requires_admin_api_key():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/applications",
            json={"name": "Test Application", "slug": "test-application"},
        )
        assert response.status_code == 401

def test_create_application():
    slug = f"test-{uuid4().hex[:12]}"

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/applications",
                json={"name": "Test Application", "slug": slug},
                headers={"X-Admin-Key": get_settings().admin_api_key},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == slug
        assert data["api_key"].startswith("aud_")

        with SessionLocal() as session:
            application = session.scalar(select(Application).where(Application.slug == slug))
            assert application is not None
            assert application.api_key_hash == hash_api_key(data["api_key"])

    finally:
        with SessionLocal() as session:
            session.execute(delete(Application).where(Application.slug == slug))
            session.commit()

