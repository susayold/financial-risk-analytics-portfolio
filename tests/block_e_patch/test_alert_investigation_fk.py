from ._helpers import E8, csv

def test_alert_investigation_fk():
    a, i = csv(E8 / "alert_log.csv"), csv(E8 / "investigation_register.csv")
    assert a.investigation_id.notna().all()
    assert set(a.investigation_id) <= set(i.investigation_id)
