import sqlite3
from unittest import mock
import pytest

import database


@pytest.fixture
def temp_db_path(tmp_path):
    # Setup temporary file path
    db_file = tmp_path / "test_app.db"

    # Patch the global DB_PATH in database module to use our temp file
    with mock.patch("database.DB_PATH", str(db_file)):
        yield db_file


def test_init_db_creates_tables(temp_db_path):
    """Verify that calling init_db successfully creates tables."""
    # Ensure database initializes without errors
    database.init_db()

    # Verify tables actually exist
    with database.get_conn() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        table_names = [row["name"] for row in tables]

        # Check a few primary tables were created successfully
        assert "projects" in table_names
        assert "checklist_items" in table_names
        assert "boq_items" in table_names
        assert "contracts" in table_names
