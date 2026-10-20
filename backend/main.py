from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Bus Stand API - Sprint 1")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Bus Stand API"}

@app.post("/routes/", response_model=schemas.Route)
def create_route(route: schemas.RouteCreate, db: Session = Depends(get_db)):
    return crud.create_route(db=db, route=route)

@app.get("/routes/", response_model=List[schemas.Route])
def read_routes(db: Session = Depends(get_db)):
    return crud.get_routes(db)

@app.post("/buses/", response_model=schemas.Bus)
def create_bus(bus: schemas.BusCreate, db: Session = Depends(get_db)):
    return crud.create_bus(db=db, bus=bus)

@app.get("/buses/", response_model=List[schemas.Bus])
def read_buses(db: Session = Depends(get_db)):
    return crud.get_buses(db)

@app.post("/bays/", response_model=schemas.Bay)
def create_bay(bay: schemas.BayCreate, db: Session = Depends(get_db)):
    return crud.create_bay(db=db, bay=bay)

@app.get("/bays/", response_model=List[schemas.Bay])
def read_bays(db: Session = Depends(get_db)):
    return crud.get_bays(db)

@app.post("/detections/", response_model=schemas.Detection)
def create_detection(detection: schemas.DetectionCreate, db: Session = Depends(get_db)):
    return crud.create_detection(db=db, detection=detection)

@app.get("/advisory/")
def get_live_advisory(db: Session = Depends(get_db)):
    return crud.get_live_advisory(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
