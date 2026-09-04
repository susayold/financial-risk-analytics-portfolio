from ._helpers import E5, csv

def test_calibration_monthly_red():
    c = csv(E5 / "calibration_monitor.csv")
    r = c[c.window_id.eq("2017-10")].iloc[0]
    assert (r.account_count, r.bad_count) == (3115, 395)
    assert r.slope == 1.3585283041585752
    a = csv(E5 / "E5_ALERTS.csv")
    assert ((a.window_id == "2017-10") & (a.metric_id == "CALIBRATION_SLOPE") & (a.severity == "RED")).any()
