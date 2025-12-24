from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class RentalItemCreate(BaseModel):
    equipment_id: int
    damage_fee: Optional[float] = 0.0


class RentalItemResponse(BaseModel):
    id: int
    equipment_id: int
    damage_fee: float


class RentalCreate(BaseModel):
    user_id: int
    employee_id: int
    start_date: date
    end_date: date
    return_date: Optional[date] = None
    items: List[RentalItemCreate]


class RentalResponse(BaseModel):
    id: int
    user_id: int
    employee_id: int
    start_date: date
    end_date: date
    return_date: Optional[date]
    status: str
    total_cost: Optional[float]
    items: List[RentalItemResponse] = []
