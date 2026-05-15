import pytest
import sqlite3
import database
from unittest import mock

@pytest.fixture
def memory_db():
    # Use a real in-memory connection since PRAGMA foreign_keys=ON is used
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # We need a custom context manager to yield the same connection
    def mock_get_conn():
        class MockConn:
            def __enter__(self):
                return conn
            def __exit__(self, exc_type, exc_val, exc_tb):
                if not exc_type:
                    conn.commit()
                # Do not close!
        return MockConn()

    with mock.patch("database.get_conn", side_effect=mock_get_conn):
        database.init_db()
        yield conn
    conn.close()

def test_save_contract_success(memory_db):
    # Setup: Create a project first because of foreign key constraint
    cur = memory_db.execute("INSERT INTO projects(name, budget) VALUES (?, ?)", ("Test Project", 1000))
    project_id = cur.lastrowid
    memory_db.commit()

    # Action
    database.save_contract(
        project_id=project_id,
        file_path="/path/to/contract.pdf",
        missing_clauses="Clause A, Clause B",
        risks_accepted=True
    )

    # Verify
    row = memory_db.execute("SELECT * FROM contracts WHERE project_id = ?", (project_id,)).fetchone()
    assert row is not None
    assert row["project_id"] == project_id
    assert row["file_path"] == "/path/to/contract.pdf"
    assert row["missing_clauses"] == "Clause A, Clause B"
    assert row["risks_accepted"] == 1

def test_save_contract_default_risks_accepted(memory_db):
    cur = memory_db.execute("INSERT INTO projects(name, budget) VALUES (?, ?)", ("Test Project", 1000))
    project_id = cur.lastrowid
    memory_db.commit()

    database.save_contract(
        project_id=project_id,
        file_path="/path/to/contract.pdf",
        missing_clauses="Clause C"
    )

    row = memory_db.execute("SELECT * FROM contracts WHERE project_id = ?", (project_id,)).fetchone()
    assert row["risks_accepted"] == 0

def test_save_contract_foreign_key_constraint(memory_db):
    # Trying to save contract for non-existent project should fail
    with pytest.raises(sqlite3.IntegrityError):
        database.save_contract(
            project_id=999,
            file_path="/path/to/contract.pdf",
            missing_clauses="Clause A"
        )
