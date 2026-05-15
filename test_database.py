import pytest
from unittest.mock import patch
import database

@pytest.fixture
def temp_db(tmp_path):
    """Fixture that provides a temporary database for testing."""
    db_path = tmp_path / "test.db"
    with patch("database.DB_PATH", str(db_path)):
        database.init_db()
        yield str(db_path)

def test_add_financial_duplicate_check(temp_db):
    """Test that add_financial prevents duplicate milestone inserts."""
    # Create a project to satisfy the foreign key constraint
    project_id = database.create_project("Test Project", 1000.0)

    # Add a milestone
    database.add_financial(project_id, 1, "Milestone A", 10.0)

    # Try adding the exact same milestone again
    database.add_financial(project_id, 1, "Milestone A", 10.0)

    # Verify that only one entry exists
    financials = database.get_financials(project_id)
    assert len(financials) == 1
    assert financials[0]["milestone_name"] == "Milestone A"
    assert financials[0]["percentage"] == 10.0
    assert financials[0]["phase_number"] == 1

def test_add_financial_multiple_records(temp_db):
    """Test that add_financial allows different milestones to be inserted."""
    # Create a project to satisfy the foreign key constraint
    project_id = database.create_project("Test Project", 1000.0)

    # Add two different milestones
    database.add_financial(project_id, 1, "Milestone A", 10.0)
    database.add_financial(project_id, 1, "Milestone B", 20.0)

    # Verify both are inserted
    financials = database.get_financials(project_id)
    assert len(financials) == 2
    names = {f["milestone_name"] for f in financials}
    assert "Milestone A" in names
    assert "Milestone B" in names
