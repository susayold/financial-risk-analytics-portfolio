from ._helpers import E5, csv

def test_e5_alert_coverage():
    a = csv(E5 / "E5_ALERTS.csv")
    assert len(a) == 16
    assert a.severity.isin(["AMBER", "RED", "CRITICAL"]).all()
