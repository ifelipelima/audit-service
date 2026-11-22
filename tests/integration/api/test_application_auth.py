from typing import Annotated
from uuid import uuid4

import pytest
from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_application
from app.core.security import generate_api_key, hash_api_key
from app.db.session import SessionLocal
from app.models.application import Application

router = APIRouter(
    dependencies=[Depends(get_current_application)]
)

@router.get("/protected")
def protected_route(
    application: Annotated[Application, Depends(get_current_application)]
):
    return {"application_id": str(application.id)}

auth_app = FastAPI()
auth_app.include_router(router)
client = TestClient(auth_app)

def test_authentication_with_valid_api_key():
    api_key = generate_api_key()

    application = Application(
        name="Test Application",
        slug=f"test-auth-{uuid4().hex[:12]}",
        api_key_hash=hash_api_key(api_key)
    )

    with SessionLocal() as session:
        session.add(application)
        session.commit()
        application_id = application.id

    try:
        response = client.get(
            "/protected",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200
        assert response.json() == {"application_id": str(application_id)}

    finally:
        with SessionLocal() as session:
            stored = session.get(Application, application_id)
            if stored is not None:
                session.delete(stored)
                session.commit()

@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"X-API-Key": "aud_invalid_key"},
    ],
)
def test_authentication_with_invalid_credentials(headers):
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401