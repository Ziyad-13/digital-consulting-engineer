import pytest
import sqlite3
import database
from unittest.mock import patch

@pytest.fixture
def mock_db_conn():
    # Patch database.get_conn() to yield a single persistent :memory: connection
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # We need a context manager that yields the same connection
    class MockGetConn:
        def __enter__(self):
            return conn
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                conn.commit()

    with patch('database.get_conn', return_value=MockGetConn()):
        database.init_db()
        yield conn

    conn.close()

def test_delete_project_cascades(mock_db_conn):
    # 1. Create two projects
    cur = mock_db_conn.execute("INSERT INTO projects (name) VALUES ('Project 1')")
    pid1 = cur.lastrowid
    cur = mock_db_conn.execute("INSERT INTO projects (name) VALUES ('Project 2')")
    pid2 = cur.lastrowid

    # 2. Insert child records for both projects in all 10 cascade tables
    for pid in (pid1, pid2):
        # checklist_items
        mock_db_conn.execute("INSERT INTO checklist_items (project_id, phase_number, item_key) VALUES (?, 1, 'chk1')", (pid,))

        # phase_status
        mock_db_conn.execute("INSERT INTO phase_status (project_id, phase_number) VALUES (?, 1)", (pid,))

        # boq_items
        mock_db_conn.execute("INSERT INTO boq_items (project_id, item_name) VALUES (?, 'item1')", (pid,))

        # contracts
        mock_db_conn.execute("INSERT INTO contracts (project_id) VALUES (?)", (pid,))

        # blueprints
        mock_db_conn.execute("INSERT INTO blueprints (project_id) VALUES (?)", (pid,))

        # siteprep_photos
        mock_db_conn.execute("INSERT INTO siteprep_photos (project_id, kind) VALUES (?, 'fencing')", (pid,))

        # materials
        mock_db_conn.execute("INSERT INTO materials (project_id, phase_number, material_key) VALUES (?, 1, 'mat1')", (pid,))

        # financials
        mock_db_conn.execute("INSERT INTO financials (project_id, phase_number) VALUES (?, 1)", (pid,))

        # payment_certificates
        mock_db_conn.execute("INSERT INTO payment_certificates (project_id, phase_number, certificate_no) VALUES (?, 1, 'cert1')", (pid,))

        # timers
        mock_db_conn.execute("INSERT INTO timers (project_id, phase_number, timer_key) VALUES (?, 1, 'timer1')", (pid,))

    mock_db_conn.commit()

    # Verify records were inserted
    for table in [
        "checklist_items", "phase_status", "boq_items", "contracts", "blueprints",
        "siteprep_photos", "materials", "financials", "payment_certificates", "timers"
    ]:
        assert mock_db_conn.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id=?", (pid1,)).fetchone()[0] == 1
        assert mock_db_conn.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id=?", (pid2,)).fetchone()[0] == 1

    # 3. Call delete_project
    database.delete_project(pid1)

    # 4. Verify Project 1 is deleted and Project 2 remains
    assert mock_db_conn.execute("SELECT COUNT(*) FROM projects WHERE id=?", (pid1,)).fetchone()[0] == 0
    assert mock_db_conn.execute("SELECT COUNT(*) FROM projects WHERE id=?", (pid2,)).fetchone()[0] == 1

    # 5. Verify cascades: Project 1 records deleted, Project 2 records remain
    for table in [
        "checklist_items", "phase_status", "boq_items", "contracts", "blueprints",
        "siteprep_photos", "materials", "financials", "payment_certificates", "timers"
    ]:
        assert mock_db_conn.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id=?", (pid1,)).fetchone()[0] == 0
        assert mock_db_conn.execute(f"SELECT COUNT(*) FROM {table} WHERE project_id=?", (pid2,)).fetchone()[0] == 1
