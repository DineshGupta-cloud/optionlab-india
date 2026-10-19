from pydantic import BaseModel
from typing import Literal

Action = Literal["BUY", "SELL"]
OptionType = Literal["CE", "PE"]


class Leg(BaseModel):
    action: Action
    option_type: OptionType
    strike: float
    premium: float
    quantity: int
