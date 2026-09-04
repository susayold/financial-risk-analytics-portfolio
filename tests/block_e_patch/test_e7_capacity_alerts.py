from ._helpers import E7, csv

def test_e7_capacity_alerts():
    a = csv(E7 / "E7_ALERTS.csv")
    assert set(a.policy) == {"GROWTH", "BALANCED"}
    assert not a.severity.eq("GREEN").any()
