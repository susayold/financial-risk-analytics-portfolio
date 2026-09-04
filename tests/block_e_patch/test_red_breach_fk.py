from ._helpers import E8, csv

def test_red_breach_fk():
    a, b = csv(E8 / "alert_log.csv"), csv(E8 / "breach_register.csv")
    red = a[a.severity.isin(["RED", "CRITICAL"])]
    assert red.alert_id.isin(b.alert_id).all()
