from sqlalchemy.orm import Session
import models, schemas

def get_routes(db: Session):
    return db.query(models.Route).all()

def create_route(db: Session, route: schemas.RouteCreate):
    db_route = models.Route(**route.model_dump())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

def get_buses(db: Session):
    return db.query(models.Bus).all()

def get_bus_by_reg(db: Session, registration_number: str):
    return db.query(models.Bus).filter(models.Bus.registration_number == registration_number).first()

def create_bus(db: Session, bus: schemas.BusCreate):
    db_bus = models.Bus(**bus.model_dump())
    db.add(db_bus)
    db.commit()
    db.refresh(db_bus)
    return db_bus

def get_bays(db: Session):
    return db.query(models.Bay).all()

def create_bay(db: Session, bay: schemas.BayCreate):
    db_bay = models.Bay(**bay.model_dump())
    db.add(db_bay)
    db.commit()
    db.refresh(db_bay)
    return db_bay

def create_detection(db: Session, detection: schemas.DetectionCreate):
    db_detection = models.Detection(**detection.model_dump())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

def get_live_advisory(db: Session):
    latest_detections = db.query(models.Detection).order_by(models.Detection.timestamp.desc()).limit(50).all()
    
    seen_buses = set()
    advisory = []
    
    for det in latest_detections:
        if det.bus_registration not in seen_buses:
            seen_buses.add(det.bus_registration)
            
            bus = get_bus_by_reg(db, det.bus_registration)
            if bus and bus.route:
                advisory.append({
                    "bus_number": bus.registration_number,
                    "destination": bus.route.destination,
                    "route_name": bus.route.route_name,
                    "fare": bus.route.fare,
                    "bay_name": det.bay.bay_name,
                    "timestamp": det.timestamp
                })
    return advisory
