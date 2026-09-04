from ._helpers import E8, csv

def test_alert_action_fk():
    a, x = csv(E8 / "alert_log.csv"), csv(E8 / "action_register.csv")
    assert a.action_id.notna().all()
    assert set(a.action_id) <= set(x.action_id)
