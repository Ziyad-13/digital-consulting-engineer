import pytest
from phase_definitions import previous_phase, next_phase, PHASE_ORDER

def test_previous_phase():
    # Test valid transitions
    assert previous_phase(PHASE_ORDER[1]) == PHASE_ORDER[0]
    assert previous_phase(PHASE_ORDER[2]) == PHASE_ORDER[1]

    # Test first phase (should return None)
    assert previous_phase(PHASE_ORDER[0]) is None

    # Test invalid phase (should return None)
    assert previous_phase(-1) is None
    assert previous_phase(999) is None

def test_next_phase():
    # Test valid transitions
    assert next_phase(PHASE_ORDER[0]) == PHASE_ORDER[1]
    assert next_phase(PHASE_ORDER[1]) == PHASE_ORDER[2]

    # Test last phase (should return None)
    assert next_phase(PHASE_ORDER[-1]) is None

    # Test invalid phase (should return None)
    assert next_phase(-1) is None
    assert next_phase(999) is None
