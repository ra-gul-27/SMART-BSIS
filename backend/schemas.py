from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

# --- BUS SCHEMAS ---
class BusBase(BaseModel):
    registration_no: str
    bus_type: str = "Standard"
    capacity: int = 45
    status: str = "Active"
    driver_name: Optional[str] = None
    last_maintenance: Optional[date] = None

class BusCreate(BusBase):
    pass

class Bus(BusBase):
    id: int
    class Config:
        from_attributes = True

# --- ROUTE SCHEMAS ---
class RouteBase(BaseModel):
    route_id: str
    source: str
    destination: str
    via_stops: Optional[str] = None
    distance_km: Optional[float] = None
    duration_mins: Optional[int] = None
    status: str = "Active"

class RouteCreate(RouteBase):
    pass

class Route(RouteBase):
    id: int
    class Config:
        from_attributes = True

# --- PARKING BAY SCHEMAS ---
class ParkingBayBase(BaseModel):
    bay_id: str
    status: str = "Available"
    vehicle_reg: Optional[str] = None
    polygon_points: Optional[str] = None

class ParkingBayCreate(ParkingBayBase):
    pass

class ParkingBay(ParkingBayBase):
    id: int
    class Config:
        from_attributes = True

# --- DETECTION SCHEMAS ---
class DetectionBase(BaseModel):
    bus_registration: str
    bay_id: str
    confidence: float

class DetectionCreate(DetectionBase):
    pass

class Detection(DetectionBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# --- ANPR SCHEMAS ---
class ANPRRecordBase(BaseModel):
    plate_number: str
    camera_loc: str = "CAM-01"
    confidence: float = 95.0
    match_status: str = "Verified"

class ANPRRecordCreate(ANPRRecordBase):
    pass

class ANPRRecord(ANPRRecordBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# --- SCHEDULE SCHEMAS ---
class ScheduleBase(BaseModel):
    bus_no: str
    route: str
    destination: str
    bay: str
    departure_time: str
    arrival_time: str
    fare: str
    status: str = "SCHEDULED"

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    class Config:
        from_attributes = True

# --- ADVISORY RESPONSE ---
class AdvisoryItem(BaseModel):
    bus_number: str
    route: str
    destination: str
    bay: str
    departure_time: str
    status: str
    fare: str
    confidence: Optional[float] = None
