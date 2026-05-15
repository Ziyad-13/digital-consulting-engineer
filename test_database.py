import pytest
import sqlite3
from unittest.mock import patch
from contextlib import contextmanager

import database

@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    @contextmanager
    def mock_get_conn():
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    with patch('database.get_conn', new=mock_get_conn):
        database.init_db()
        conn.execute("INSERT INTO projects (id, name) VALUES (1, 'Test Project')")
        conn.commit()
        yield conn

    conn.close()

def test_set_boq_items_inserts_and_deletes(in_memory_db):
    project_id = 1

    initial_items = [
        {"item_name": "Concrete", "quantity": 10.5, "unit": "m3", "category": "structural"}
    ]

    # Use the function being tested
    database.set_boq_items(project_id, initial_items)

    # Verify insertion
    cursor = in_memory_db.execute("SELECT * FROM boq_items WHERE project_id=?", (project_id,))
    results = [dict(row) for row in cursor.fetchall()]
    assert len(results) == 1
    assert results[0]["item_name"] == "Concrete"
    assert results[0]["quantity"] == 10.5

    # Insert new items, which should delete the old ones
    new_items = [
        {"item_name": "Steel", "quantity": 5.0, "unit": "ton", "category": "structural"},
        {"item_name": "Wood", "quantity": 100.0, "unit": "kg", "category": "architectural"}
    ]
    database.set_boq_items(project_id, new_items)

    # Verify deletion and new insertion
    cursor = in_memory_db.execute("SELECT * FROM boq_items WHERE project_id=? ORDER BY id", (project_id,))
    results = [dict(row) for row in cursor.fetchall()]

    assert len(results) == 2
    assert results[0]["item_name"] == "Steel"
    assert results[1]["item_name"] == "Wood"

def test_set_boq_items_empty_list(in_memory_db):
    project_id = 1

    initial_items = [
        {"item_name": "Concrete", "quantity": 10.5, "unit": "m3", "category": "structural"}
    ]
    database.set_boq_items(project_id, initial_items)

    # Insert empty list
    database.set_boq_items(project_id, [])

    # Verify all items are deleted
    cursor = in_memory_db.execute("SELECT * FROM boq_items WHERE project_id=?", (project_id,))
    results = cursor.fetchall()
    assert len(results) == 0

def test_set_boq_items_missing_category_defaults(in_memory_db):
    project_id = 1

    items_missing_category = [
        {"item_name": "Sand", "quantity": 10.0, "unit": "kg"}
    ]

    database.set_boq_items(project_id, items_missing_category)

    cursor = in_memory_db.execute("SELECT * FROM boq_items WHERE project_id=?", (project_id,))
    results = [dict(row) for row in cursor.fetchall()]

    assert len(results) == 1
    assert results[0]["item_name"] == "Sand"
    # category should default to structural
    assert results[0]["category"] == "structural"
