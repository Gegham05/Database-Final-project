from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

# This line is now removed as Alembic handles database schema creation.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gegham Auto Service API")

# --- Cars Endpoints ---

@app.post("/cars/", response_model=schemas.Car, tags=["Cars"])
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    return crud.create_car(db=db, car=car)

@app.get("/cars/", response_model=List[schemas.Car], tags=["Cars"])
def read_cars(skip: int = 0, limit: int = 100, sort_by_year: Optional[str] = Query(None, enum=["asc", "desc"]), db: Session = Depends(get_db)):
    cars = crud.get_cars(db, skip=skip, limit=limit, sort_by_year=sort_by_year)
    return cars

@app.get("/cars/search/", response_model=List[schemas.Car], tags=["Cars"])
def search_cars(make: str, year: int, db: Session = Depends(get_db)):
    """
    Search for cars with multiple conditions (make and year).
    """
    cars = crud.get_cars_by_make_and_year(db, make=make, year=year)
    return cars

@app.get("/cars/{car_id}", response_model=schemas.Car, tags=["Cars"])
def read_car(car_id: int, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

@app.put("/cars/{car_id}", response_model=schemas.Car, tags=["Cars"])
def update_car(car_id: int, car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = crud.update_car(db, car_id=car_id, car=car)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

@app.delete("/cars/{car_id}", response_model=schemas.Car, tags=["Cars"])
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = crud.delete_car(db, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car

# --- Mechanics Endpoints ---

@app.post("/mechanics/", response_model=schemas.Mechanic, tags=["Mechanics"])
def create_mechanic(mechanic: schemas.MechanicCreate, db: Session = Depends(get_db)):
    return crud.create_mechanic(db=db, mechanic=mechanic)

@app.get("/mechanics/", response_model=List[schemas.Mechanic], tags=["Mechanics"])
def read_mechanics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    mechanics = crud.get_mechanics(db, skip=skip, limit=limit)
    return mechanics

@app.get("/mechanics/stats/orders", response_model=List[schemas.MechanicOrderStats], tags=["Mechanics"])
def get_mechanic_order_stats(db: Session = Depends(get_db)):
    """
    Get the number of orders per mechanic (GROUP BY).
    """
    return crud.get_orders_per_mechanic(db)

@app.get("/mechanics/{mechanic_id}", response_model=schemas.Mechanic, tags=["Mechanics"])
def read_mechanic(mechanic_id: int, db: Session = Depends(get_db)):
    db_mechanic = crud.get_mechanic(db, mechanic_id=mechanic_id)
    if db_mechanic is None:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return db_mechanic

@app.put("/mechanics/{mechanic_id}", response_model=schemas.Mechanic, tags=["Mechanics"])
def update_mechanic(mechanic_id: int, mechanic: schemas.MechanicCreate, db: Session = Depends(get_db)):
    db_mechanic = crud.update_mechanic(db, mechanic_id=mechanic_id, mechanic=mechanic)
    if db_mechanic is None:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return db_mechanic

@app.delete("/mechanics/{mechanic_id}", response_model=schemas.Mechanic, tags=["Mechanics"])
def delete_mechanic(mechanic_id: int, db: Session = Depends(get_db)):
    db_mechanic = crud.delete_mechanic(db, mechanic_id=mechanic_id)
    if db_mechanic is None:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return db_mechanic

# --- Orders Endpoints ---

@app.post("/orders/", response_model=schemas.Order, tags=["Orders"])
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@app.get("/orders/", response_model=List[schemas.Order], tags=["Orders"])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

@app.get("/orders/details/", response_model=List[schemas.OrderWithDetails], tags=["Orders"])
def read_orders_with_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of orders with full car and mechanic details (JOIN).
    """
    orders = crud.get_orders_with_details(db, skip=skip, limit=limit)
    return orders

@app.get("/orders/{order_id}", response_model=schemas.OrderWithDetails, tags=["Orders"])
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.put("/orders/update-costs-by-car/{car_id}", tags=["Orders"])
def update_costs_for_car(car_id: int, new_cost: float, db: Session = Depends(get_db)):
    """
    Update the cost of all orders for a specific car (UPDATE with condition).
    """
    return crud.update_order_costs_for_car(db, car_id=car_id, new_cost=new_cost)


@app.put("/orders/{order_id}", response_model=schemas.Order, tags=["Orders"])
def update_order(order_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = crud.update_order(db, order_id=order_id, order=order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.delete("/orders/{order_id}", response_model=schemas.Order, tags=["Orders"])
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.delete_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.get("/orders/search-details/", response_model=List[schemas.Order], tags=["Orders"])
def search_orders_by_details(q: str, db: Session = Depends(get_db)):
    """
    Full-text search in order work details.
    """
    return crud.search_orders_by_details(db, query=q)
