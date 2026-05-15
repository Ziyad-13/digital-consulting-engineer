import pytest
from unittest.mock import patch
import sqlite3
import database

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # We yield a context manager that returns the same persistent connection
    class MockConnectionContext:
        def __enter__(self):
            return conn
        def __exit__(self, exc_type, exc_val, exc_tb):
            conn.commit()

    with patch("database.get_conn", return_value=MockConnectionContext()):
        database.init_db()
        # Create a dummy project since project_id is a foreign key
        database.create_project("Test Project", 100000)
        yield conn
        conn.close()

def test_upsert_material_new(db_conn):
    # Test inserting a new material with minimal parameters
    database.upsert_material(1, 1, "MAT1", material_name="Cement", expected_qty=100.0, expected_unit="bags")

    materials = database.get_materials(1, 1)
    assert "MAT1" in materials
    mat1 = materials["MAT1"]
    assert mat1["material_name"] == "Cement"
    assert mat1["expected_qty"] == 100.0
    assert mat1["expected_unit"] == "bags"
    assert mat1["delivered_qty"] is None
    assert mat1["match_status"] == database.MATCH_PENDING
    assert mat1["delivered_at"] is None

def test_upsert_material_new_with_invoice(db_conn):
    # Test inserting a new material with an invoice (sets delivered_at)
    database.upsert_material(1, 1, "MAT2", invoice_path="path/to/inv.pdf")

    materials = database.get_materials(1, 1)
    assert "MAT2" in materials
    mat2 = materials["MAT2"]
    assert mat2["invoice_path"] == "path/to/inv.pdf"
    assert mat2["delivered_at"] is not None

def test_upsert_material_update_existing(db_conn):
    # Create initial material
    database.upsert_material(1, 1, "MAT1", material_name="Cement", expected_qty=100.0)

    # Update specific values
    database.upsert_material(1, 1, "MAT1", delivered_qty=50.0, invoice_path="inv1.pdf", match_status=database.MATCH_OK)

    materials = database.get_materials(1, 1)
    mat1 = materials["MAT1"]
    assert mat1["material_name"] == "Cement" # unchanged
    assert mat1["expected_qty"] == 100.0     # unchanged
    assert mat1["delivered_qty"] == 50.0
    assert mat1["invoice_path"] == "inv1.pdf"
    assert mat1["match_status"] == database.MATCH_OK
    assert mat1["delivered_at"] is not None

def test_upsert_material_update_none(db_conn):
    # Create initial material with some values
    database.upsert_material(1, 1, "MAT1", material_name="Cement", expected_qty=100.0, invoice_path="inv1.pdf")
    materials = database.get_materials(1, 1)
    mat1_initial = materials["MAT1"]

    # Update with all None values for optional fields (except material_key, project_id, phase)
    database.upsert_material(1, 1, "MAT1", material_name=None, expected_qty=None, delivered_qty=None)

    materials_after = database.get_materials(1, 1)
    mat1_after = materials_after["MAT1"]

    # Ensure values were not overwritten with None
    assert mat1_after["material_name"] == "Cement"
    assert mat1_after["expected_qty"] == 100.0
    assert mat1_after["invoice_path"] == "inv1.pdf"
    assert mat1_after["delivered_at"] == mat1_initial["delivered_at"]
