from app.db.base import Base
from app.models import Application


def test_application_model_is_registered():
    assert Application.__table__.name in Base.metadata.tables

def test_application_unique_constraints():
    columns = Application.__table__.columns
    assert columns['slug'].unique is True
    assert columns['api_key_hash'].unique is True

def test_application_required_fields():
    columns = Application.__table__.columns
    assert columns['name'].nullable is False
    assert columns['slug'].nullable is False
    assert columns['api_key_hash'].nullable is False

def test_application_indexed_fields():
    columns = Application.__table__.columns
    assert columns['slug'].index is True