from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models.schemas import Leg, AnalyzeRequest, AnalyzeResponse, Point, Metrics
from .services import payoff as payoff_service

app = FastAPI(title="OptionLab India — Paper Mode API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "mode": "DEMO DATA — PAPER MODE"}


@app.get("/api/v1/market/underlyings")
def underlyings():
    # Demo only
    return {
        "underlyings": [
            {"symbol": "NIFTY 50", "spot": 25000.0},
            {"symbol": "BANKNIFTY", "spot": 44400.0},
            {"symbol": "FINNIFTY", "spot": 2500.0},
        ],
        "note": "DEMO DATA — PAPER MODE",
    }


@app.get("/api/v1/market/option-chain")
def option_chain(underlying: str = Query("NIFTY 50")):
    # Return a small, static option chain for demo use
    # Marked as DEMO DATA
    strikes = [24800, 24900, 25000, 25100, 25200, 25300]
    rows = []
    for s in strikes:
        rows.append(
            {
                "strike": s,
                "call": {"oi": 10000 + s % 500, "ltp": max(0, (25000 - s) * 0.1 + 100), "volume": (s % 100) + 10},
                "put": {"oi": 8000 + s % 400, "ltp": max(0, (s - 25000) * 0.12 + 80), "volume": (s % 120) + 5},
            }
        )
    return {"underlying": underlying, "timestamp": "DEMO DATA", "rows": rows, "note": "DEMO DATA — PAPER MODE"}


@app.get("/api/v1/strategies/templates")
def templates():
    # Predefined sample templates (small)
    return {
        "templates": [
            {
                "name": "Long Call",
                "legs": [{"action": "BUY", "option_type": "CE", "strike": 25000, "premium": 150, "quantity": 1}],
            },
            {
                "name": "Long Put",
                "legs": [{"action": "BUY", "option_type": "PE", "strike": 25000, "premium": 120, "quantity": 1}],
            },
            {
                "name": "Sample Spread (example strategy)",
                "legs": [
                    {"action": "BUY", "option_type": "CE", "strike": 25000, "premium": 150, "quantity": 1},
                    {"action": "SELL", "option_type": "CE", "strike": 25200, "premium": 70, "quantity": 1},
                ],
                "spot": 25000,
            },
        ]
    }


@app.post("/api/v1/strategies/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest):
    legs = [Leg(**l.dict()) for l in payload.legs]
    if not legs:
        raise HTTPException(status_code=400, detail="At least one leg required")
    result = payoff_service.analyze_strategy(
        legs=legs, spot=payload.spot, range_min=payload.range_min, range_max=payload.range_max, steps=payload.steps
    )
    points = [Point(**p) for p in result["points"]]
    m = result["metrics"]
    metrics = Metrics(
        net_premium_debit=m["net_premium_debit"],
        maximum_profit=m["maximum_profit"],
        maximum_loss=m["maximum_loss"],
        breakevens=m["breakevens"],
        bounded=m["bounded"],
    )
    return AnalyzeResponse(points=points, metrics=metrics)
