from datetime import datetime

from pydantic import BaseModel


class ProfileCreate(BaseModel):
    full_name: str
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    fitness_level: str
    goals: str
    available_days: str
    equipment: str
    health_notes: str | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None
    gender: str | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    fitness_level: str | None = None
    goals: str | None = None
    available_days: str | None = None
    equipment: str | None = None
    health_notes: str | None = None


class ProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    fitness_level: str
    goals: str
    available_days: str
    equipment: str
    health_notes: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}
