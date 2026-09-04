from ._helpers import E5, csv

def test_performance_sample_gate():
    p = csv(E5 / "calibration_persistence_input.csv")
    assert p.sample_eligible.eq(True).all()
    assert not p[p.sample_eligible.eq(False)].status.isin(["GREEN", "AMBER", "RED"]).any()
