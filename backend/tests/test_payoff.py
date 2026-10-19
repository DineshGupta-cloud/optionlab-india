import math
from app.services.types import Leg
from app.services import payoff as ps


def test_long_call_payoff():
    legs = [Leg(action="BUY", option_type="CE", strike=100.0, premium=10.0, quantity=1)]
    res = ps.analyze_strategy(legs, spot=100.0, range_min=50.0, range_max=200.0, steps=151)
    # max loss is premium = -10 (at or below strike)
    assert math.isclose(res["metrics"]["maximum_loss"], -10.0, rel_tol=1e-4)
    # unlimited profit expected (long call); metric should show None for maximum_profit
    assert res["metrics"]["maximum_profit"] is None


def test_long_put_payoff():
    legs = [Leg(action="BUY", option_type="PE", strike=100.0, premium=8.0, quantity=1)]
    res = ps.analyze_strategy(legs, spot=100.0, range_min=0.0, range_max=200.0, steps=151)
    assert math.isclose(res["metrics"]["maximum_loss"], -8.0, rel_tol=1e-4)
    # long put is bounded on upside (towards zero price it can be large profit) -> maximum_profit might be within sampled range or None
    # we assert that max loss equals -premium
    assert res["metrics"]["maximum_loss"] == -8.0


def test_short_call_and_short_put():
    # Short naked call -> unlimited risk (loss)
    legs = [Leg(action="SELL", option_type="CE", strike=100.0, premium=5.0, quantity=1)]
    res = ps.analyze_strategy(legs, spot=100.0, range_min=50.0, range_max=1000.0, steps=201)
    assert res["metrics"]["maximum_loss"] is None  # unlimited loss to the upside

    # Short naked put -> unlimited risk (loss) to downside
    legs = [Leg(action="SELL", option_type="PE", strike=100.0, premium=5.0, quantity=1)]
    res = ps.analyze_strategy(legs, spot=100.0, range_min=0.0, range_max=200.0, steps=201)
    assert res["metrics"]["maximum_loss"] is None


def test_bull_call_spread_and_bear_put_spread():
    # Bull call spread (buy 100 CE @10, sell 110 CE @4)
    legs = [
        Leg(action="BUY", option_type="CE", strike=100.0, premium=10.0, quantity=1),
        Leg(action="SELL", option_type="CE", strike=110.0, premium=4.0, quantity=1),
    ]
    res = ps.analyze_strategy(legs, spot=105.0, range_min=80.0, range_max=140.0, steps=161)
    # net premium debit 6
    assert math.isclose(res["metrics"]["net_premium_debit"], 6.0, rel_tol=1e-4)
    # max profit = (110 - 100) - net debit = 4
    assert math.isclose(res["metrics"]["maximum_profit"], 4.0, rel_tol=1e-3)

    # Bear put spread (buy 110P @12, sell 100P @5)
    legs = [
        Leg(action="BUY", option_type="PE", strike=110.0, premium=12.0, quantity=1),
        Leg(action="SELL", option_type="PE", strike=100.0, premium=5.0, quantity=1),
    ]
    res = ps.analyze_strategy(legs, spot=105.0, range_min=50.0, range_max=140.0, steps=181)
    # net premium debit 7
    assert math.isclose(res["metrics"]["net_premium_debit"], 7.0, rel_tol=1e-4)


def test_straddle():
    legs = [
        Leg(action="BUY", option_type="CE", strike=100.0, premium=6.0, quantity=1),
        Leg(action="BUY", option_type="PE", strike=100.0, premium=5.0, quantity=1),
    ]
    res = ps.analyze_strategy(legs, spot=100.0, range_min=50.0, range_max=150.0, steps=201)
    # net premium debit 11
    assert math.isclose(res["metrics"]["net_premium_debit"], 11.0, rel_tol=1e-6)
    # maximum_loss should equal -11
    assert math.isclose(res["metrics"]["maximum_loss"], -11.0, rel_tol=1e-6)


def test_multiple_leg_aggregation_and_breakeven_sample_strategy():
    # Sample strategy from spec:
    # BUY CE strike 25000 premium 150 qty1
    # SELL CE strike 25200 premium 70 qty1
    legs = [
        Leg(action="BUY", option_type="CE", strike=25000.0, premium=150.0, quantity=1),
        Leg(action="SELL", option_type="CE", strike=25200.0, premium=70.0, quantity=1),
    ]
    res = ps.analyze_strategy(legs, spot=25000.0, range_min=24700.0, range_max=25500.0, steps=161)

    # Net premium debit = 150 - 70 = 80 per unit
    assert math.isclose(res["metrics"]["net_premium_debit"], 80.0, rel_tol=1e-6)

    # Maximum loss = net premium debit = -80? Note: conventions in engine use positive debit, P&L values are profit numbers.
    # Our engine returns maximum_loss as a numeric value (lowest P&L). For this spread, minimum P&L is -80
    assert math.isclose(res["metrics"]["maximum_loss"], -80.0, rel_tol=1e-4)

    # Maximum profit = difference in strikes - net debit = 200 - 80 = 120
    assert math.isclose(res["metrics"]["maximum_profit"], 120.0, rel_tol=1e-3)

    # Upper breakeven = 25000 + 80 = 25080
    bps = res["metrics"]["breakevens"]
    assert any(abs(b - 25080.0) < 1.0 for b in bps)
