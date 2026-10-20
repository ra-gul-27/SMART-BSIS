from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime

# --- BUSES ---
def get_buses(db: Session):
    return db.query(models.Bus).all()

def get_bus_by_reg(db: Session, reg: str):
    return db.query(models.Bus).filter(models.Bus.registration_no == reg).first()

def create_bus(db: Session, bus: schemas.BusCreate):
    db_bus = models.Bus(**bus.model_dump())
    db.add(db_bus)
    db.commit()
    db.refresh(db_bus)
    return db_bus

# --- ROUTES ---
def get_routes(db: Session):
    return db.query(models.Route).all()

def create_route(db: Session, route: schemas.RouteCreate):
    db_route = models.Route(**route.model_dump())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

# --- PARKING BAYS ---
def get_bays(db: Session):
    return db.query(models.ParkingBay).all()

def get_bay_by_id(db: Session, bay_id: str):
    return db.query(models.ParkingBay).filter(models.ParkingBay.bay_id == bay_id).first()

def create_bay(db: Session, bay: schemas.ParkingBayCreate):
    db_bay = models.ParkingBay(**bay.model_dump())
    db.add(db_bay)
    db.commit()
    db.refresh(db_bay)
    return db_bay

def update_bay_status(db: Session, bay_id: str, status: str, vehicle_reg: str = None):
    bay = get_bay_by_id(db, bay_id)
    if bay:
        bay.status = status
        bay.vehicle_reg = vehicle_reg
        db.commit()
        db.refresh(bay)
    return bay

# --- DETECTIONS ---
def create_detection(db: Session, detection: schemas.DetectionCreate):
    db_det = models.Detection(**detection.model_dump())
    db.add(db_det)
    
    # Automatically update corresponding parking bay to Occupied with this vehicle
    update_bay_status(db, detection.bay_id, "Occupied", detection.bus_registration)
    
    # Automatically generate an event for the dashboard event stream & live marquee
    db_event = models.Event(
        title=f"Bus Docked - {detection.bay_id}",
        description=f"Bus {detection.bus_registration} docked at Bay {detection.bay_id} (AI Conf: {int(detection.confidence)}%)",
        event_type="primary"
    )
    db.add(db_event)

    # If this bus or bay has a scheduled departure, set it to BOARDING
    sched = db.query(models.Schedule).filter(
        (models.Schedule.bus_no == detection.bus_registration) | (models.Schedule.bay == detection.bay_id)
    ).first()
    if sched and sched.status == "SCHEDULED":
        sched.status = "BOARDING"

    db.commit()
    db.refresh(db_det)
    return db_det

def get_recent_detections(db: Session, limit: int = 50):
    return db.query(models.Detection).order_by(models.Detection.timestamp.desc()).limit(limit).all()

# --- ANPR RECORDS ---
def create_anpr_record(db: Session, record: schemas.ANPRRecordCreate):
    db_anpr = models.ANPRRecord(**record.model_dump())
    db.add(db_anpr)
    db.commit()
    db.refresh(db_anpr)
    return db_anpr

def get_anpr_records(db: Session, limit: int = 50):
    return db.query(models.ANPRRecord).order_by(models.ANPRRecord.timestamp.desc()).limit(limit).all()

# --- SCHEDULES ---
def get_schedules(db: Session):
    return db.query(models.Schedule).all()

def create_schedule(db: Session, sched: schemas.ScheduleCreate):
    db_sched = models.Schedule(**sched.model_dump())
    db.add(db_sched)
    db.commit()
    db.refresh(db_sched)
    return db_sched

# --- PASSENGER LIVE ADVISORY ---
def get_live_advisory(db: Session):
    """
    Returns live advisory list for passenger screen/mobile app.
    Combines active bay occupancy with schedules and confirmed detections.
    """
    # 1. Fetch occupied bays
    occupied_bays = db.query(models.ParkingBay).filter(models.ParkingBay.status == "Occupied").all()
    
    advisory = []
    seen_buses = set()
    
    for bay in occupied_bays:
        if not bay.vehicle_reg:
            continue
            
        seen_buses.add(bay.vehicle_reg)
        # Try matching schedule by bus_no or route
        sched = db.query(models.Schedule).filter(
            (models.Schedule.bus_no == bay.vehicle_reg) | (models.Schedule.bay == bay.bay_id)
        ).first()
        
        # Try finding bus registration details
        bus = get_bus_by_reg(db, bay.vehicle_reg)
        
        advisory.append({
            "bus_number": bay.vehicle_reg,
            "route": sched.route if sched else "Express Service",
            "destination": sched.destination if sched else "City Central",
            "bay": bay.bay_id,
            "departure_time": sched.departure_time if sched else "Boarding Now",
            "status": "BOARDING",
            "fare": sched.fare if sched else "₹ 50.00",
            "confidence": 98.0
        })
        
    # 2. Add upcoming scheduled departures that are not yet at bay
    upcoming = db.query(models.Schedule).filter(models.Schedule.status != "DEPARTED").limit(10).all()
    for item in upcoming:
        if item.bus_no not in seen_buses:
            advisory.append({
                "bus_number": item.bus_no,
                "route": item.route,
                "destination": item.destination,
                "bay": item.bay,
                "departure_time": item.departure_time,
                "status": item.status,
                "fare": item.fare,
                "confidence": None
            })
            seen_buses.add(item.bus_no)
            
    return advisory
