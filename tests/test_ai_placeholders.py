import pytest
from ai_placeholders import estimate_boq, CAT_STRUCT, CAT_INSUL, CAT_MEP, CAT_ELEC, CAT_SANI, CAT_FINISH

def test_estimate_boq_defaults():
    blueprint_data = {
        "total_built_area_m2": 320,
        "floors": 2,
    }
    boq = estimate_boq(blueprint_data)
    assert len(boq) > 0
    # verify it returns a list of dictionaries with correct keys
    assert all(isinstance(item, dict) for item in boq)
    assert all(set(item.keys()) == {"item_name", "quantity", "unit", "category"} for item in boq)

    # check if items have correct categories
    categories = {item["category"] for item in boq}
    assert categories == {CAT_STRUCT, CAT_INSUL, CAT_MEP, CAT_ELEC, CAT_SANI, CAT_FINISH}

    # Check default finish level is "economic" and affects tiles/paint
    tile_item = next(item for item in boq if "Floor Tiles" in item["item_name"])
    assert "Ceramic" in tile_item["item_name"]
    paint_item = next(item for item in boq if "Interior Paint" in item["item_name"])
    assert "Standard" in paint_item["item_name"]
    assert "2 coats" in paint_item["item_name"]

def test_estimate_boq_luxury():
    blueprint_data = {"total_built_area_m2": 400, "floors": 3}
    boq = estimate_boq(blueprint_data, finish_level="luxury")

    tile_item = next(item for item in boq if "Floor Tiles" in item["item_name"])
    assert "Porcelain / Marble" in tile_item["item_name"]

    paint_item = next(item for item in boq if "Interior Paint" in item["item_name"])
    assert "Premium washable" in paint_item["item_name"]
    assert "3 coats" in paint_item["item_name"]

    facade_item = next(item for item in boq if "Stone Cladding" in item["item_name"])
    assert "natural" in facade_item["item_name"]

def test_estimate_boq_custom_floors_area():
    blueprint_data = {"total_built_area_m2": 150} # no floors

    # without floor override, should default to 1
    boq = estimate_boq(blueprint_data)
    blocks_10cm = next(item for item in boq if "Concrete Blocks — 10 cm" in item["item_name"])
    assert blocks_10cm["quantity"] == 150 * 4 * 1

    # with floor override
    boq = estimate_boq(blueprint_data, floors=4)
    blocks_10cm = next(item for item in boq if "Concrete Blocks — 10 cm" in item["item_name"])
    assert blocks_10cm["quantity"] == 150 * 4 * 4

def test_estimate_boq_missing_area_floors():
    # Empty blueprint data
    blueprint_data = {}
    boq = estimate_boq(blueprint_data)

    # Should default to area=300, floors=1
    blocks_10cm = next(item for item in boq if "Concrete Blocks — 10 cm" in item["item_name"])
    assert blocks_10cm["quantity"] == 300 * 4 * 1

def test_estimate_boq_edge_cases():
    blueprint_data = {"total_built_area_m2": 0, "floors": 0}
    boq = estimate_boq(blueprint_data)

    concrete = next(item for item in boq if "Ready-mix Concrete" in item["item_name"])
    assert concrete["quantity"] == 0

    blocks_10cm = next(item for item in boq if "Concrete Blocks — 10 cm" in item["item_name"])
    assert blocks_10cm["quantity"] == 0

def test_estimate_boq_invalid_finish_level():
    blueprint_data = {"total_built_area_m2": 300, "floors": 1}
    with pytest.raises(KeyError):
        estimate_boq(blueprint_data, finish_level="unsupported_level")
