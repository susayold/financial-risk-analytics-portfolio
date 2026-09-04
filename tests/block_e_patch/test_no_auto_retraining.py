from ._helpers import E8, csv

def test_no_auto_retraining():
    assert not csv(E8 / "action_register.csv").action_type.eq("AUTO_RETRAIN").any()
    assert not csv(E8 / "action_register.csv").model_change_required.any()
