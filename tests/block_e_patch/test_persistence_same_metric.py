from ._helpers import E5, csv

def test_persistence_same_metric():
    p = csv(E5 / "calibration_persistence_input.csv")
    assert p.groupby("persistence_key").metric_id.nunique().max() == 1
