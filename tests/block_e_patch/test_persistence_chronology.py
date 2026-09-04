from ._helpers import E5, csv

def test_persistence_chronology():
    p = csv(E5 / "calibration_persistence_input.csv")
    assert p.groupby("persistence_key").window_order.apply(lambda s: s.is_monotonic_increasing).all()
