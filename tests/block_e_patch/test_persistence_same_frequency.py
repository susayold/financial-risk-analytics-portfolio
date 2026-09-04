from ._helpers import E5, csv

def test_persistence_same_frequency():
    p = csv(E5 / "calibration_persistence_input.csv")
    assert p.groupby("persistence_key").frequency.nunique().max() == 1
