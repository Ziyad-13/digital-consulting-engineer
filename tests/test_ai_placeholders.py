import pytest
from ai_placeholders import parse_blueprint_pdf

def test_parse_blueprint_pdf():
    # Test with a typical valid string file path
    result = parse_blueprint_pdf("dummy/path/to/blueprint.pdf")

    # Verify the returned dictionary has the expected keys and values
    assert isinstance(result, dict)
    assert result["total_built_area_m2"] == 320
    assert result["floors"] == 2
    assert result["rooms_detected"] == 8

    # Ensure structural_elements contains the expected sub-keys and values
    assert "structural_elements" in result
    structural_elements = result["structural_elements"]
    assert isinstance(structural_elements, dict)
    assert structural_elements["columns"] == 24
    assert structural_elements["beams"] == 36
    assert structural_elements["slabs"] == 2

def test_parse_blueprint_pdf_empty_path():
    # Test with an empty string file path, function currently just returns static dict
    result = parse_blueprint_pdf("")
    assert result["total_built_area_m2"] == 320
    assert result["floors"] == 2

def test_parse_blueprint_pdf_different_path():
    # Test with a different path, just to ensure the static dict is still returned
    result = parse_blueprint_pdf("another/file/path.pdf")
    assert result["total_built_area_m2"] == 320
    assert result["floors"] == 2
