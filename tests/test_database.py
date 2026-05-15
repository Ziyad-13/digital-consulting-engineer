import pytest
import sqlite3
import contextlib
from unittest.mock import patch
import database

@pytest.fixture
def memory_db():
    """
    Setup an in-memory SQLite database, patched over `database.get_conn()`.
    Provides a persistent connection for tests so data isn't lost between calls.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    @contextlib.contextmanager
    def _mock_get_conn():
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    with patch("database.get_conn", side_effect=_mock_get_conn):
        database.init_db()
        yield conn

    conn.close()

def test_delete_project_cascade(memory_db):
    """
    Test that deleting a project cascades correctly across all child tables.
    """
    # 1. Create a parent project
    pid = database.create_project("Test Project", 1000.0, "Test Location")

    # 2. Add related data across all known child tables
    database.upsert_checklist_item(pid, 1, "test_item", "PASS", "img_path", "rework_path")
    database.mark_phase_complete(pid, 1)
    database.set_boq_items(pid, [{"item_name": "Concrete", "quantity": 100, "unit": "m3", "category": "materials"}])
    database.save_contract(pid, "contract_path", "Missing clause 1")
    database.save_blueprint(pid, "blueprint_path")
    database.save_siteprep_photo(pid, "fencing", "fencing_path")
    database.upsert_material(pid, 1, "Cement", "MATCH", "invoice_path")
    database.add_financial(pid, "PAYMENT", 100.0, "Phase 1 completion")
    database.save_payment_certificate(pid, 1, "CERT-001", 10.0, 100.0, "cert_path")
    database.add_timer(pid, 1, "rework_timer", "Rework Duration", 3600)

    # 3. Verify data was inserted into all child tables dynamically
    cur = memory_db.cursor()

    # Find all tables that have project_id as a column (which are our child tables)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'projects'")
    all_tables = [row[0] for row in cur.fetchall()]

    child_tables = []
    for table in all_tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = [row['name'] for row in cur.fetchall()]
        if 'project_id' in columns:
            child_tables.append(table)

    # Ensure we caught the ones we expect at minimum
    assert len(child_tables) >= 10, "Expected to find at least 10 child tables"

    for table in child_tables:
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id = ?", (pid,))
        count = cur.fetchone()[0]
        assert count > 0, f"Table {table} should have data before deletion"

    cur.execute("SELECT COUNT(*) FROM projects WHERE id = ?", (pid,))
    assert cur.fetchone()[0] == 1, "Project should exist before deletion"

    # 4. Delete the project
    database.delete_project(pid)

    # 5. Verify ALL data is deleted via ON DELETE CASCADE
    for table in child_tables:
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id = ?", (pid,))
        count = cur.fetchone()[0]
        assert count == 0, f"Table {table} should be empty after cascade delete"

    cur.execute("SELECT COUNT(*) FROM projects WHERE id = ?", (pid,))
    assert cur.fetchone()[0] == 0, "Project should be deleted"
