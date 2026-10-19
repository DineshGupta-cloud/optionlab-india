from typing import List, Tuple, Optional
import numpy as np
from .types import Leg

# We'll implement payoff engine functions here.
# Each leg is: action ('BUY'|'SELL'), option_type ('CE'|'PE'), strike, premium, quantity


def option_payoff_per_unit(option_type: str, strike: float, price: float) -> float:
    if option_type == "CE":
        return max(price - strike, 0.0)
    else:
        # PE
        return max(strike - price, 0.0)


def leg_pnl_at_price(leg: Leg, price: float) -> float:
    payoff = option_payoff_per_unit(leg.option_type, leg.strike, price)
    if leg.action == "BUY":
        pnl_unit = payoff - leg.premium
    else:  # SELL
        pnl_unit = leg.premium - payoff
    return pnl_unit * leg.quantity


def total_pnl_at_price(legs: List[Leg], price: float) -> float:
    return sum(leg_pnl_at_price(l, price) for l in legs)


def compute_curve(
    legs: List[Leg], spot: float, range_min: Optional[float], range_max: Optional[float], steps: int = 201
) -> Tuple[List[Tuple[float, float]], float, float]:
    # Choose defaults if range not specified: around spot ± 15%
    if range_min is None:
        range_min = max(1.0, spot * 0.7)
    if range_max is None:
        range_max = spot * 1.3 if spot > 0 else 100.0
    prices = np.linspace(range_min, range_max, num=steps)
    pnls = [total_pnl_at_price(legs, float(p)) for p in prices]
    return list(zip(prices.tolist(), pnls)), float(prices[0]), float(prices[-1])


def detect_unbounded(legs: List[Leg]) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (unbounded_upward, unbounded_downward) where values may be 'profit', 'loss', or None.
    Upward refers to behavior as price -> +inf (right tail).
    Downward refers to behavior as price -> 0 (left tail).
    """
    net_call_qty = 0
    net_put_qty = 0
    for l in legs:
        mult = 1 if l.action == "BUY" else -1
        if l.option_type == "CE":
            net_call_qty += mult * l.quantity
        else:
            net_put_qty += mult * l.quantity

    # Right tail (price -> +inf): calls dominate
    if net_call_qty > 0:
        right = "profit"
    elif net_call_qty < 0:
        right = "loss"
    else:
        right = None

    # Left tail (price -> 0): puts dominate. For puts, payoff ~ -p * net_put_qty (since put payoff ≈ strike - p).
    # If net_put_qty > 0 (net long puts) => as p->0 pnl -> +inf (profit). If net_put_qty < 0 => loss.
    if net_put_qty > 0:
        left = "profit"
    elif net_put_qty < 0:
        left = "loss"
    else:
        left = None

    return right, left


def find_breakevens(points: List[Tuple[float, float]]) -> List[float]:
    # points: list of (price, pnl)
    breakevens = []
    for (p1, v1), (p2, v2) in zip(points, points[1:]):
        if v1 == 0.0:
            breakevens.append(p1)
        if v1 * v2 < 0:
            # linear interpolate to find root
            bp = p1 - v1 * (p2 - p1) / (v2 - v1)
            breakevens.append(float(bp))
    # Deduplicate sorted
    breakevens = sorted(set(round(b, 6) for b in breakevens))
    return breakevens


def analyze_strategy(
    legs: List[Leg], spot: float, range_min: Optional[float], range_max: Optional[float], steps: int = 201
) -> dict:
    points, pmin, pmax = compute_curve(legs, spot, range_min, range_max, steps)
    prices = [p for p, _ in points]
    pnls = [v for _, v in points]

    net_premium_paid = sum((l.premium * l.quantity) if l.action == "BUY" else -(l.premium * l.quantity) for l in legs)
    # net_premium_debit: positive means net paid (debit)
    net_premium_debit = net_premium_paid

    # metrics from sample curve
    max_pnl = max(pnls)
    min_pnl = min(pnls)

    # detect unbounded
    right, left = detect_unbounded(legs)
    maximum_profit = None if right == "profit" or left == "profit" and max_pnl == max_pnl else max_pnl
    maximum_loss = None if right == "loss" or left == "loss" and min_pnl == min_pnl else min_pnl

    # We'll say bounded if neither tail is unbounded in loss or profit direction.
    bounded = not (right is not None or left is not None and (left is not None))

    breakevens = find_breakevens(points)

    return {
        "points": [{"price": float(p), "pnl": float(v)} for p, v in points],
        "metrics": {
            "net_premium_debit": float(net_premium_debit),
            "maximum_profit": None if (right == "profit" or left == "profit") else float(max_pnl),
            "maximum_loss": None if (right == "loss" or left == "loss") else float(min_pnl),
            "breakevens": breakevens,
            "bounded": (right is None and left is None),
        },
    }
