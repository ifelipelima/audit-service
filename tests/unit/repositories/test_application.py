from unittest.mock import Mock

from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.application import ApplicationRepository


def test_create_application():
    session = Mock(spec=Session)
    repository = ApplicationRepository(session)

    application = repository.create(name="Test Application", slug="test-application", api_key_hash="a" * 64)

    assert isinstance(application, Application)
    assert application.name == "Test Application"
    assert application.slug == "test-application"
    assert application.api_key_hash == "a" * 64

    session.add.assert_called_once_with(application)
    session.commit.assert_not_called()

def test_get_by_slug_existing_application():
    session = Mock(spec=Session)
    expected = Application(name="Test Application", slug="test-application", api_key_hash="a" * 64)
    session.scalar.return_value = expected

    repository = ApplicationRepository(session)
    result = repository.get_by_slug("test-application")

    assert result is expected
    session.scalar.assert_called_once()
    
    statement = session.scalar.call_args.args[0]
    assert "test-application" in statement.compile().params.values()

def test_get_application_by_api_key_hash():
    session = Mock(spec=Session)
    expected = Application(name="Test Application", slug="test-application", api_key_hash="a" * 64)
    session.scalar.return_value = expected

    repository = ApplicationRepository(session)
    result = repository.get_by_api_key_hash("a" * 64)

    assert result is expected
    statement = session.scalar.call_args.args[0]
    assert "a" * 64 in statement.compile().params.values()