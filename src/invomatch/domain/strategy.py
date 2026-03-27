from __future__ import annotations

from pydantic import BaseModel, Field


class StrategyContext(BaseModel):
    reference_weight: float = Field(default=1.0, gt=0.0)
    amount_weight: float = Field(default=1.0, gt=0.0)
    date_weight: float = Field(default=1.0, gt=0.0)

    allow_partial_matching: bool = True