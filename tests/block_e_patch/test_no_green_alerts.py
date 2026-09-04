from ._helpers import E8, csv

def test_no_green_alerts():
    assert not csv(E8 / "alert_log.csv").severity.eq("GREEN").any()
