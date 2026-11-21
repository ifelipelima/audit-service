import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

def verify_admin_key(api_key: Annotated[str | None, Depends(admin_key_header)]):
    expected_key = get_settings().admin_api_key

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrative credentials",
        )