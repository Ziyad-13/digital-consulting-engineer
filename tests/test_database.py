import sqlite3
import pytest
from datetime import datetime

import database


def test_mark_phase_complete_success():
    """Test successfully marking a phase as complete."""
    # Create a project first (required due to foreign key constraints)
    project_id = database.create_project("Test Project", 100000.0)

    # Initially, phase should not be marked as complete
    assert not database.is_phase_marked_complete(project_id, 1)

    # Mark the phase as complete
    database.mark_phase_complete(project_id, 1)

    # Now it should be complete
    assert database.is_phase_marked_complete(project_id, 1)

    # Verify completed_at timestamp is set
    with database.get_conn() as conn:
        row = conn.execute(
            "SELECT completed_at FROM phase_status WHERE project_id=? AND phase_number=?",
            (project_id, 1)
        ).fetchone()
        assert row is not None
        assert row["completed_at"] is not None

        # Verify it's a valid ISO formatted timestamp
        datetime.fromisoformat(row["completed_at"])

def test_mark_phase_complete_invalid_project():
    """Test that marking a phase complete for a non-existent project raises IntegrityError."""
    # We do not create a project, so project_id 9999 should not exist
    invalid_project_id = 9999

    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        database.mark_phase_complete(invalid_project_id, 1)

    assert "FOREIGN KEY constraint failed" in str(exc_info.value)

def test_mark_phase_complete_idempotent_updates():
    """Test that multiple calls to mark_phase_complete update the timestamp but don't duplicate records."""
    project_id = database.create_project("Another Test Project", 50000.0)

    # First call
    database.mark_phase_complete(project_id, 1)

    with database.get_conn() as conn:
        row1 = conn.execute(
            "SELECT completed_at FROM phase_status WHERE project_id=? AND phase_number=?",
            (project_id, 1)
        ).fetchone()
        first_timestamp = row1["completed_at"]

        # Verify only one row exists for this project/phase
        count1 = conn.execute(
            "SELECT COUNT(*) as c FROM phase_status WHERE project_id=? AND phase_number=?",
            (project_id, 1)
        ).fetchone()["c"]
        assert count1 == 1

    # Second call (simulate later time by tweaking database manually or just rely on OR REPLACE)
    database.mark_phase_complete(project_id, 1)

    with database.get_conn() as conn:
        row2 = conn.execute(
            "SELECT completed_at FROM phase_status WHERE project_id=? AND phase_number=?",
            (project_id, 1)
        ).fetchone()
        second_timestamp = row2["completed_at"]

        # Verify only one row still exists for this project/phase
        count2 = conn.execute(
            "SELECT COUNT(*) as c FROM phase_status WHERE project_id=? AND phase_number=?",
            (project_id, 1)
        ).fetchone()["c"]
        assert count2 == 1

        # Because datetime is recorded with timespec="seconds",
        # these timestamps could be identical if the second call happens in the same second.
        # But we at least verify it didn't create a new record and didn't crash.
        assert first_timestamp <= second_timestamp
