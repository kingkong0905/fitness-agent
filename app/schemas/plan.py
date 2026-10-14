from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


class PlanGenerateRequest(BaseModel):
    week_start: date
    extra_notes: str | None = None


class PlanOut(BaseModel):
    id: int
    user_id: int
    title: str
    week_start: date
    generated_plan: dict[str, Any]
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PlanListItem(BaseModel):
    id: int
    title: str
    week_start: date
    created_at: datetime

    model_config = {"from_attributes": True}
