from ._helpers import E8, csv

def test_change_control_portfolio_approval():
    c = csv(E8 / "change_control_register.csv")
    assert c.approved_for_portfolio_use.eq(True).all()
