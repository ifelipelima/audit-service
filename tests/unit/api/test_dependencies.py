from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_application
from app.core.security import hash_api_key
from app.models.application import Application


def test_get_current_application_with_valid_key():
    session = Mock(spec=Session)
    application = Application(name="Test Application", slug="test-application", api_key_hash=hash_api_key("aud_valid_key"))
    session.scalar.return_value = application

    result = get_current_application("aud_valid_key", session)

    assert result is application

@pytest.mark.parametrize("api_key", [None, "invalid_key"])
def test_get_current_application_with_invalid_key(api_key):
    session = Mock(spec=Session)
    session.scalar.return_value = None

    with pytest.raises(HTTPException) as exc:
        get_current_application(api_key, session)

    assert exc.value.status_code == 401