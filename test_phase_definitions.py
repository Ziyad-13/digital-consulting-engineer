import pytest
from phase_definitions import next_phase

def test_next_phase_beginning():
    # 0 is the first phase in PHASE_ORDER
    assert next_phase(0) == 1

def test_next_phase_middle():
    # Test a phase in the middle
    assert next_phase(3) == 4

def test_next_phase_end():
    # 6 is the last phase, so next_phase should return None
    assert next_phase(6) is None

def test_next_phase_invalid():
    # -1 is not in PHASE_ORDER
    assert next_phase(-1) is None
    # 7 is not in PHASE_ORDER
    assert next_phase(7) is None
