from ._helpers import E8, csv

def test_kri_alert_separation():
    k, a = csv(E8 / "kri_register.csv"), csv(E8 / "alert_log.csv")
    assert len(k) > len(a)
    assert k.status.eq("GREEN").any()
