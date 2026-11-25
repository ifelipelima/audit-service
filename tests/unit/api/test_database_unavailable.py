from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.main import app


def failing_db():
    raise OperationalError("SELECT 1", {}, Exception("connection refused"))
    yield  # pragma: no cover


def test_returns_503_when_database_is_unavailable():
    app.dependency_overrides[get_db] = failing_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/events", headers={"X-API-Key": "aud_any"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "Persistence service unavailable."}
