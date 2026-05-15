import os
import tempfile
import pytest
import database

@pytest.fixture(autouse=True)
def setup_test_db():
    # Create a temporary file for the database
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Override the DB_PATH in database module
    original_db_path = database.DB_PATH
    database.DB_PATH = temp_db_path

    # Initialize the database schema
    database.init_db()

    yield temp_db_path

    # Restore the original DB_PATH
    database.DB_PATH = original_db_path

    # Clean up the temporary file
    try:
        os.remove(temp_db_path)
    except OSError:
        pass
