import pytest
import sqlite3
import os

import database

@pytest.fixture
def temp_db(tmp_path):
    """
    Setup an isolated database for testing.
    Using a temporary file instead of :memory: because get_conn
    opens and closes connections per call, and :memory: databases
    are destroyed when the connection closes unless shared cache is used.
    """
    db_file = tmp_path / "test_app.db"

    # Patch DB_PATH in database module
    original_db_path = database.DB_PATH
    database.DB_PATH = str(db_file)

    # Initialize the schema
    database.init_db()

    yield str(db_file)

    # Restore original path
    database.DB_PATH = original_db_path

def test_create_project_success(temp_db):
    """Test that a project is correctly inserted into the database."""
    # Act
    project_id = database.create_project(name="Test Villa", budget=1500000.50, location="Riyadh")

    # Assert
    assert isinstance(project_id, int)
    assert project_id > 0

    # Verify via DB directly
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row["name"] == "Test Villa"
    assert row["budget"] == 1500000.50
    assert row["location"] == "Riyadh"
    assert row["current_phase"] == 0 # Default from schema

def test_create_project_default_location(temp_db):
    """Test that project creation works with default location."""
    # Act - Omitting location argument
    project_id = database.create_project(name="Default Location Project", budget=500000.0)

    # Assert
    assert isinstance(project_id, int)

    # Verify via DB directly
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row["name"] == "Default Location Project"
    assert row["budget"] == 500000.0
    assert row["location"] == "" # Default from function signature
