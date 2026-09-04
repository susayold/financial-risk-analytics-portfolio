from ._helpers import E8, E9, csv, js

def test_redevelopment_decision_logic():
    d = js(E9 / "BLOCK_E_DECISION_PATCHED.json")
    t = csv(E8 / "redevelopment_trigger_log.csv")
    assert d["redevelopment_candidate"] is False
    assert t.status.eq("NOT_TRIGGERED").all()
