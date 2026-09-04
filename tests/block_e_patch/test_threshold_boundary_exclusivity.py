from ._helpers import E0, csv

def test_threshold_boundary_exclusivity():
    t = csv(E0 / "E0_THRESHOLD_REGISTER.csv").set_index("metric_id")
    assert "x < 0.25" in t.loc["PSI", "amber_rule"]
    assert t.loc["PSI", "red_rule"] == "x >= 0.25"
