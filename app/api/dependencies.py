import secrets
from typing import Annotated

from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings
from app.core.security import hash_api_key
from app.db.session import get_db
from app.models.application import Application
from app.repositories.application import ApplicationRepository

admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)
application_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_admin_key(api_key: Annotated[str | None, Depends(admin_key_header)]):
    expected_key = get_settings().admin_api_key

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative credentials",
        )

def get_current_application(
        api_key: Annotated[str | None, Depends(application_key_header)],
        session: Annotated[Session, Depends(get_db)]
) -> Application: 
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid application credentials"
        )

    api_key_hash = hash_api_key(api_key)
    application = ApplicationRepository(session).get_by_api_key_hash(api_key_hash)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid application credentials"
        )

    return application