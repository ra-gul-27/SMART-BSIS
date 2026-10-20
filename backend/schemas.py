from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RouteBase(BaseModel):
    route_name: str
    source: str
    destination: str
    fare: float

class RouteCreate(RouteBase):
    pass

class Route(RouteBase):
    id: int
    class Config:
        from_attributes = True

class BusBase(BaseModel):
    registration_number: str
    active_status: bool = True

class BusCreate(BusBase):
    route_id: int

class Bus(BusBase):
    id: int
    route_id: int
    route: Route
    class Config:
        from_attributes = True

class BayBase(BaseModel):
    bay_name: str
    polygon_points: str
    active_status: bool = True

class BayCreate(BayBase):
    pass

class Bay(BayBase):
    id: int
    class Config:
        from_attributes = True

class DetectionBase(BaseModel):
    bus_registration: str
    bay_id: int
    confidence: float

class DetectionCreate(DetectionBase):
    pass

class Detection(DetectionBase):
    id: int
    timestamp: datetime
    bay: Bay
    class Config:
        from_attributes = True
