from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from .database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True)
    year = Column(Integer)
    vin = Column(String, unique=True, index=True)
    owner_name = Column(String)
    
    orders = relationship("Order", back_populates="car")

class Mechanic(Base):
    __tablename__ = "mechanics"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    experience = Column(Integer)
    rank = Column(String)
    employee_id = Column(String, unique=True, index=True)
    phone_number = Column(String(20), nullable=True)
    
    orders = relationship("Order", back_populates="mechanic")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    issue_date = Column(Date, nullable=False)
    cost = Column(Numeric(10, 2))
    work_type = Column(String)
    planned_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    work_details = Column(JSON, nullable=True)

    car_id = Column(Integer, ForeignKey("cars.id"))
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"))

    car = relationship("Car", back_populates="orders")
    mechanic = relationship("Mechanic", back_populates="orders")
