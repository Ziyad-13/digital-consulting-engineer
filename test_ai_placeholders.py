import pytest
from ai_placeholders import estimate_boq

def test_estimate_boq_economic():
    blueprint_data = {"total_built_area_m2": 320, "floors": 2}
    boq = estimate_boq(blueprint_data, finish_level="economic")

    assert len(boq) > 0

    # Check that structural items exist
    structural = [item for item in boq if item["category"] == "structural"]
    assert len(structural) > 0

    # Check that finishes exist and have expected paint/tile grades
    finishes = [item for item in boq if item["category"] == "finishes"]
    assert len(finishes) > 0

    # Assert paint row string
    paint_row = next(item for item in finishes if "Interior Paint" in item["item_name"])
    assert "Standard" in paint_row["item_name"]
    assert "2 coats" in paint_row["item_name"]

    # Assert tile row string
    tile_row = next(item for item in finishes if "Floor Tiles" in item["item_name"])
    assert "Ceramic" in tile_row["item_name"]


def test_estimate_boq_luxury():
    blueprint_data = {"total_built_area_m2": 450, "floors": 3}
    boq = estimate_boq(blueprint_data, finish_level="luxury")

    assert len(boq) > 0

    # Check finishes
    finishes = [item for item in boq if item["category"] == "finishes"]

    # Assert paint row string
    paint_row = next(item for item in finishes if "Interior Paint" in item["item_name"])
    assert "Premium washable" in paint_row["item_name"]
    assert "3 coats" in paint_row["item_name"]

    # Assert tile row string
    tile_row = next(item for item in finishes if "Floor Tiles" in item["item_name"])
    assert "Porcelain / Marble" in tile_row["item_name"]

    # Assert facade cladding
    stone_row = next(item for item in finishes if "Stone Cladding" in item["item_name"])
    assert "natural" in stone_row["item_name"]
    assert "manufactured" not in stone_row["item_name"]


def test_estimate_boq_no_floors_provided():
    blueprint_data = {"total_built_area_m2": 150} # "floors" not provided
    boq = estimate_boq(blueprint_data)

    assert len(boq) > 0

    structural = [item for item in boq if item["category"] == "structural"]
    assert len(structural) > 0
