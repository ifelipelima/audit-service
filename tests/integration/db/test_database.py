from sqlalchemy import text

from app.db.session import engine

def test_database_connection():
    with engine.connect() as connection:
        result = connection.scalar(text("SELECT 1"))

        assert result == 1