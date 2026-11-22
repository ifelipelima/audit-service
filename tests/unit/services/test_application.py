from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_api_key
from app.models.application import Application
from app.repositories.application import ApplicationRepository
from app.schemas.application import ApplicationCreate
from app.services.application import ApplicationAlreadyExistsError, ApplicationService


@pytest.fixture
def session():
    return Mock(spec=Session)

@pytest.fixture
def repository():
    return Mock(spec=ApplicationRepository)

@pytest.fixture
def service(session, repository):
    instance = ApplicationService(session)
    instance.repository = repository
    return instance

@pytest.fixture
def application_data():
    return ApplicationCreate(name="Test Application", slug="test-application")

def test_create_application_success(service, session, repository, application_data):
    repository.get_by_slug.return_value = None
    repository.create.side_effect = lambda **kwargs: Application(**kwargs)

    application, api_key = service.create(application_data)

    assert application.name == application_data.name
    assert application.slug == application_data.slug
    assert application.api_key_hash == hash_api_key(api_key)
    assert api_key.startswith("aud_")

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(application)

def test_create_application_already_exists(service, session, repository, application_data):
    repository.get_by_slug.return_value = Application(name="Existing", slug=application_data.slug, api_key_hash="a" * 64)

    with pytest.raises(ApplicationAlreadyExistsError):
        service.create(application_data)

    repository.create.assert_not_called()
    session.commit.assert_not_called()

def test_create_application_with_concurrent_duplicate(service, session, repository, application_data):
    repository.get_by_slug.side_effect = [None, Application(name="Existing", slug=application_data.slug, api_key_hash="a" * 64)]
    session.commit.side_effect = IntegrityError(statement="INSERT INTO application", params={}, orig=Exception("duplicate key"))

    with pytest.raises(ApplicationAlreadyExistsError):
        service.create(application_data)

    session.rollback.assert_called_once()
    session.refresh.assert_not_called()

def test_create_application_with_other_integrity_error(service, session, repository, application_data):
    repository.get_by_slug.side_effect = [None, None]
    session.commit.side_effect = IntegrityError(statement="INSERT INTO application", params={}, orig=Exception("integrity violation"))

    with pytest.raises(IntegrityError):
        service.create(application_data)

    session.rollback.assert_called_once()
