import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime
from database import Base

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key=True, index=True)
    registration_no = Column(String, unique=True, index=True)
    bus_type = Column(String, default="Standard")
    capacity = Column(Integer, default=45)
    status = Column(String, default="Active")
    driver_name = Column(String, nullable=True)
    last_maintenance = Column(Date, nullable=True)

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, unique=True, index=True)
    source = Column(String)
    destination = Column(String)
    via_stops = Column(String, nullable=True)
    distance_km = Column(Float, nullable=True)
    duration_mins = Column(Integer, nullable=True)
    status = Column(String, default="Active")

class ParkingBay(Base):
    __tablename__ = "parking_bays"
    id = Column(Integer, primary_key=True, index=True)
    bay_id = Column(String, unique=True, index=True)
    status = Column(String, default="Available")
    vehicle_reg = Column(String, nullable=True)
    polygon_points = Column(String, nullable=True)  # JSON formatted polygon: "[[x1,y1],[x2,y2],...]"

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, index=True)
    bus_registration = Column(String, index=True)
    bay_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    confidence = Column(Float)

class ANPRRecord(Base):
    __tablename__ = "anpr_records"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    plate_number = Column(String, index=True)
    camera_loc = Column(String, default="CAM-01")
    confidence = Column(Float, default=95.0)
    match_status = Column(String, default="Verified")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    bus_no = Column(String, index=True)
    route = Column(String)
    destination = Column(String)
    bay = Column(String)
    departure_time = Column(String)
    arrival_time = Column(String)
    fare = Column(String)
    status = Column(String, default="SCHEDULED")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    title = Column(String)
    description = Column(String, nullable=True)
    event_type = Column(String, default="primary")
