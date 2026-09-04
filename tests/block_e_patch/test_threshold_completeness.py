from ._helpers import E0, csv

def test_threshold_completeness():
    t = csv(E0 / "E0_THRESHOLD_REGISTER.csv")
    assert len(t) == 12
    assert t.green_rule.notna().all() and t.amber_rule.notna().all() and t.red_rule.notna().all()
