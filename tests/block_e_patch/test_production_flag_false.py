from ._helpers import E8, csv

def test_production_flag_false():
    c = csv(E8 / "change_control_register.csv")
    assert c.production_authorization.eq(False).all()
    assert c.regulatory_compliance_claimed.eq(False).all()
