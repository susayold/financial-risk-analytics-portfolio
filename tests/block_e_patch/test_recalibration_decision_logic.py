from ._helpers import E9, js

def test_recalibration_decision_logic():
    d = js(E9 / "BLOCK_E_DECISION_PATCHED.json")
    assert d["recalibration_candidate"] is True
