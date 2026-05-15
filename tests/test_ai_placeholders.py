import pytest
from ai_placeholders import run_material_match

def test_run_material_match_missing_inputs():
    # missing invoice
    res = run_material_match(100.0, "m2", 100.0, None)
    assert res["status"] == "PENDING"

    # missing delivered_qty
    res = run_material_match(100.0, "m2", None, "path/to/invoice.pdf")
    assert res["status"] == "PENDING"

    # zero or negative delivered_qty
    res = run_material_match(100.0, "m2", 0.0, "path/to/invoice.pdf")
    assert res["status"] == "PENDING"

    res = run_material_match(100.0, "m2", -5.0, "path/to/invoice.pdf")
    assert res["status"] == "PENDING"

def test_run_material_match_exact():
    res = run_material_match(100.0, "m2", 100.0, "path/to/invoice.pdf")
    assert res["status"] == "MATCH"
    assert res["delta_pct"] == 0.0

def test_run_material_match_within_tolerance():
    # +9%
    res = run_material_match(100.0, "m2", 109.0, "path/to/invoice.pdf")
    assert res["status"] == "MATCH"
    assert pytest.approx(res["delta_pct"]) == 9.0

    # -9%
    res = run_material_match(100.0, "m2", 91.0, "path/to/invoice.pdf")
    assert res["status"] == "MATCH"
    assert pytest.approx(res["delta_pct"]) == -9.0

def test_run_material_match_on_boundary():
    # +10%
    res = run_material_match(100.0, "m2", 110.0, "path/to/invoice.pdf")
    assert res["status"] == "MATCH"
    assert pytest.approx(res["delta_pct"]) == 10.0

    # -10%
    res = run_material_match(100.0, "m2", 90.0, "path/to/invoice.pdf")
    assert res["status"] == "MATCH"
    assert pytest.approx(res["delta_pct"]) == -10.0

def test_run_material_match_outside_tolerance():
    # +11%
    res = run_material_match(100.0, "m2", 111.0, "path/to/invoice.pdf")
    assert res["status"] == "MISMATCH"
    assert pytest.approx(res["delta_pct"]) == 11.0

    # -11%
    res = run_material_match(100.0, "m2", 89.0, "path/to/invoice.pdf")
    assert res["status"] == "MISMATCH"
    assert pytest.approx(res["delta_pct"]) == -11.0

def test_run_material_match_zero_expected():
    # expected_qty is 0, but delivered qty is positive
    res = run_material_match(0.0, "m2", 10.0, "path/to/invoice.pdf")
    assert res["status"] == "MISMATCH"
    assert res["delta_pct"] is None
    assert "Expected qty is 0" in res["reason"]
