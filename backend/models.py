from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String, unique=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    active_status = Column(Boolean, default=True)

    route = relationship("Route", back_populates="buses")

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String, index=True)
    source = Column(String)
    destination = Column(String)
    fare = Column(Float)

    buses = relationship("Bus", back_populates="route")

class Bay(Base):
    __tablename__ = "bays"
    id = Column(Integer, primary_key=True, index=True)
    bay_name = Column(String, index=True)
    polygon_points = Column(String) # Stored as JSON string "[ [x,y], [x,y] ]"
    active_status = Column(Boolean, default=True)
    
class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, index=True)
    bus_registration = Column(String, index=True)
    bay_id = Column(Integer, ForeignKey("bays.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    confidence = Column(Float)
    
    bay = relationship("Bay")
