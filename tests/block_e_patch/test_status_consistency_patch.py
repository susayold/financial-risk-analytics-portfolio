from ._helpers import E9, js

def test_status_consistency_patch():
    d, s = js(E9 / "BLOCK_E_DECISION_PATCHED.json"), js(E9 / "BLOCK_E_FINAL_SCORECARD_PATCHED.json")
    assert d["status"] == s["status"] == "PASS_WITH_MONITORING"
    assert d["canonical_tag"] == "block-e-v1.0.1-final"
