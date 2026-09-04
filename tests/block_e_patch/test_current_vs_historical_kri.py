from ._helpers import E9, js

def test_current_vs_historical_kri():
    d = js(E9 / "BLOCK_E_DECISION_PATCHED.json")
    assert d["highest_current_kri_status"] == "AMBER"
    assert d["highest_observed_kri_status"] == "RED"
