from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Action = Literal["BUY", "SELL"]
OptionType = Literal["CE", "PE"]


class Leg(BaseModel):
    action: Action
    option_type: OptionType
    strike: float = Field(..., ge=0)
    premium: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)


class AnalyzeRequest(BaseModel):
    legs: List[Leg]
    spot: float = Field(..., ge=0)
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    steps: Optional[int] = 201  # number of points in returned curve


class Point(BaseModel):
    price: float
    pnl: float


class Metrics(BaseModel):
    net_premium_debit: float
    maximum_profit: Optional[float]  # None means unlimited
    maximum_loss: Optional[float]    # None means unlimited
    breakevens: List[float]
    bounded: bool


class AnalyzeResponse(BaseModel):
    points: List[Point]
    metrics: Metrics
