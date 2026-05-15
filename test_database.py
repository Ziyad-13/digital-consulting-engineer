import os
import tempfile
import sqlite3
import pytest
from unittest.mock import patch

import database
from database import STATUS_PENDING, STATUS_PASS, STATUS_FAIL, STATUS_REWORK

@pytest.fixture
def temp_db():
    # Create a temporary file for the database
    fd, path = tempfile.mkstemp()

    # Patch the DB_PATH to use the temporary file
    with patch("database.DB_PATH", path):
        # Initialize the database schema
        database.init_db()

        yield path

    # Clean up after the test
    os.close(fd)
    os.unlink(path)

def get_item(project_id, phase, item_key):
    with database.get_conn() as conn:
        return conn.execute(
            "SELECT * FROM checklist_items WHERE project_id=? AND phase_number=? AND item_key=?",
            (project_id, phase, item_key)
        ).fetchone()

def test_upsert_checklist_item_insert(temp_db):
    """Test inserting a new checklist item and verifying default values."""
    project_id = database.create_project("Test Project", 100000, "Test Location")
    phase = 1
    item_key = "test_item_1"

    # Insert new item
    database.upsert_checklist_item(project_id, phase, item_key)

    # Verify it was inserted with default values
    item = get_item(project_id, phase, item_key)
    assert item is not None
    assert item["status"] == STATUS_PENDING
    assert item["notes"] == ""
    assert item["image_path"] is None
    assert item["rework_count"] == 0

def test_upsert_checklist_item_insert_with_values(temp_db):
    """Test inserting a new checklist item with specific values."""
    project_id = database.create_project("Test Project 2", 100000, "Test Location")
    phase = 1
    item_key = "test_item_2"
    status = STATUS_FAIL
    notes = "Initial failure"
    image_path = "/path/to/image.jpg"
    rework_count = 1

    # Insert new item with values
    database.upsert_checklist_item(
        project_id, phase, item_key,
        status=status, notes=notes, image_path=image_path, rework_count=rework_count
    )

    # Verify values
    item = get_item(project_id, phase, item_key)
    assert item is not None
    assert item["status"] == status
    assert item["notes"] == notes
    assert item["image_path"] == image_path
    assert item["rework_count"] == rework_count

def test_upsert_checklist_item_update_all_fields(temp_db):
    """Test updating all fields of an existing checklist item."""
    project_id = database.create_project("Test Project 3", 100000, "Test Location")
    phase = 1
    item_key = "test_item_3"

    # Initial insert
    database.upsert_checklist_item(project_id, phase, item_key)

    # Update all fields
    new_status = STATUS_REWORK
    new_notes = "Needs rework"
    new_image_path = "/path/to/rework.jpg"
    new_rework_count = 1

    database.upsert_checklist_item(
        project_id, phase, item_key,
        status=new_status, notes=new_notes, image_path=new_image_path, rework_count=new_rework_count
    )

    # Verify updates
    item = get_item(project_id, phase, item_key)
    assert item is not None
    assert item["status"] == new_status
    assert item["notes"] == new_notes
    assert item["image_path"] == new_image_path
    assert item["rework_count"] == new_rework_count

def test_upsert_checklist_item_partial_updates(temp_db):
    """Test updating an item multiple times with partial updates (some parameters None)."""
    project_id = database.create_project("Test Project 4", 100000, "Test Location")
    phase = 1
    item_key = "test_item_4"

    # Initial insert with specific values
    initial_status = STATUS_FAIL
    initial_notes = "First attempt"
    initial_image_path = "/path/to/fail.jpg"

    database.upsert_checklist_item(
        project_id, phase, item_key,
        status=initial_status, notes=initial_notes, image_path=initial_image_path
    )

    # Partial update: just the status
    new_status = STATUS_REWORK
    database.upsert_checklist_item(project_id, phase, item_key, status=new_status)

    item = get_item(project_id, phase, item_key)
    assert item["status"] == new_status
    # Other fields should remain untouched
    assert item["notes"] == initial_notes
    assert item["image_path"] == initial_image_path
    assert item["rework_count"] == 0 # Default value from insert

    # Partial update: just the notes and rework_count
    new_notes = "Working on it"
    new_rework_count = 1
    database.upsert_checklist_item(
        project_id, phase, item_key,
        notes=new_notes, rework_count=new_rework_count
    )

    item = get_item(project_id, phase, item_key)
    assert item["status"] == new_status # Should remain unchanged from previous update
    assert item["notes"] == new_notes
    assert item["image_path"] == initial_image_path # Should remain unchanged
    assert item["rework_count"] == new_rework_count
