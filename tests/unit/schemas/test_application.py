import pytest
from pydantic import ValidationError

from app.schemas.application import ApplicationCreate


def test_application_create_valid_data():
    application = ApplicationCreate(name="Test Application", slug="test-application")
    assert application.name == "Test Application"
    assert application.slug == "test-application"

@pytest.mark.parametrize(
    "slug",
    [
        "invalid slug",
        "InvalidSlug",
        "invalid_slug",
        "invalid-slug-",
        "-invalid-slug",
        "a" * 81,
    ],
)
def test_application_create_invalid_slug(slug):
    with pytest.raises(ValidationError):
        ApplicationCreate(name="Test Application", slug=slug)

@pytest.mark.parametrize("name", ["", "A", "a" * 121])
def test_application_create_invalid_name(name):
    with pytest.raises(ValidationError):
        ApplicationCreate(name=name, slug="valid-slug")