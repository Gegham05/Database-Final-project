from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from . import models, schemas
from typing import Optional, List

# --- Car CRUD ---

def get_car(db: Session, car_id: int):
    return db.query(models.Car).filter(models.Car.id == car_id).first()

def get_cars(db: Session, skip: int = 0, limit: int = 100, sort_by_year: Optional[str] = None):
    query = db.query(models.Car)
    if sort_by_year:
        if sort_by_year.lower() == 'desc':
            query = query.order_by(desc(models.Car.year))
        else:
            query = query.order_by(models.Car.year)
    return query.offset(skip).limit(limit).all()

def get_cars_by_make_and_year(db: Session, make: str, year: int):
    return db.query(models.Car).filter(models.Car.make == make, models.Car.year == year).all()

def create_car(db: Session, car: schemas.CarCreate):
    db_car = models.Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

def update_car(db: Session, car_id: int, car: schemas.CarCreate):
    db_car = get_car(db, car_id)
    if db_car:
        for key, value in car.dict().items():
            setattr(db_car, key, value)
        db.commit()
        db.refresh(db_car)
    return db_car

def delete_car(db: Session, car_id: int):
    db_car = get_car(db, car_id)
    if db_car:
        db.delete(db_car)
        db.commit()
    return db_car

# --- Mechanic CRUD ---

def get_mechanic(db: Session, mechanic_id: int):
    return db.query(models.Mechanic).filter(models.Mechanic.id == mechanic_id).first()

def get_mechanics(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Mechanic).offset(skip).limit(limit).all()

def create_mechanic(db: Session, mechanic: schemas.MechanicCreate):
    db_mechanic = models.Mechanic(**mechanic.dict())
    db.add(db_mechanic)
    db.commit()
    db.refresh(db_mechanic)
    return db_mechanic

def update_mechanic(db: Session, mechanic_id: int, mechanic: schemas.MechanicCreate):
    db_mechanic = get_mechanic(db, mechanic_id)
    if db_mechanic:
        for key, value in mechanic.dict().items():
            setattr(db_mechanic, key, value)
        db.commit()
        db.refresh(db_mechanic)
    return db_mechanic

def delete_mechanic(db: Session, mechanic_id: int):
    db_mechanic = get_mechanic(db, mechanic_id)
    if db_mechanic:
        db.delete(db_mechanic)
        db.commit()
    return db_mechanic

# --- Order CRUD ---

def get_order(db: Session, order_id: int):
    return db.query(models.Order).options(joinedload(models.Order.car), joinedload(models.Order.mechanic)).filter(models.Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

def get_orders_with_details(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).options(joinedload(models.Order.car), joinedload(models.Order.mechanic)).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: int, order: schemas.OrderCreate):
    db_order = get_order(db, order_id)
    if db_order:
        for key, value in order.dict().items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
    return db_order

def update_order_costs_for_car(db: Session, car_id: int, new_cost: float):
    db.query(models.Order).filter(models.Order.car_id == car_id).update({"cost": new_cost})
    db.commit()
    return {"message": f"Costs for car {car_id} updated."}


def delete_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
    return db_order

def get_orders_per_mechanic(db: Session) -> List[dict]:
    return db.query(models.Mechanic.full_name, func.count(models.Order.id).label("order_count")) \
             .join(models.Order, models.Mechanic.id == models.Order.mechanic_id) \
             .group_by(models.Mechanic.full_name) \
             .all()

def search_orders_by_details(db: Session, query: str):
    return db.query(models.Order).filter(models.Order.work_details.op('->>')('description').ilike(f"%{query}%")).all()
