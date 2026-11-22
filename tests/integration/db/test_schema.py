import pytest
from sqlalchemy import inspect

from app.db.session import engine


@pytest.mark.parametrize("table_name", ["applications", "audit_events"])
def test_database_tables_exist(table_name):
    inspector = inspect(engine)
    assert inspector.has_table(table_name)

