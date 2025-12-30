from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal

# --- Car Schemas ---

class CarBase(BaseModel):
    make: str
    year: int
    vin: str
    owner_name: str

class CarCreate(CarBase):
    pass

class Car(CarBase):
    id: int

    class Config:
        orm_mode = True

# --- Mechanic Schemas ---

class MechanicBase(BaseModel):
    full_name: str
    experience: int
    rank: str
    employee_id: str
    phone_number: Optional[str] = None

class MechanicCreate(MechanicBase):
    pass

class Mechanic(MechanicBase):
    id: int

    class Config:
        orm_mode = True

# --- Order Schemas ---

class OrderBase(BaseModel):
    issue_date: date
    cost: Decimal
    work_type: str
    planned_completion_date: date
    actual_completion_date: Optional[date] = None
    car_id: int
    mechanic_id: int
    work_details: Optional[dict] = None

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int

    class Config:
        orm_mode = True

# Schemas for relationships
class OrderWithDetails(Order):
    car: Car
    mechanic: Mechanic

class CarWithOrders(Car):
    orders: List[Order] = []

class MechanicWithOrders(Mechanic):
    orders: List[Order] = []

# --- Stats Schemas ---
class MechanicOrderStats(BaseModel):
    full_name: str
    order_count: int

    class Config:
        orm_mode = True
