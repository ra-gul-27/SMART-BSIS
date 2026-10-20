import os
import sys
import io
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Add paths for models and vision
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

import models, schemas, crud
from database import SessionLocal, engine, get_db
from vision.bay_logic import BayManager
from vision.yolo_detector import YOLOBusDetector
from vision.anpr_engine import ANPREngine
from vision.camera import VideoCamera

# Create tables if not present
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Bus Stand Information System API",
    description="REST API and AI Computer Vision Pipeline for Bus Detection, ANPR, and Bay Mapping.",
    version="2.0.0"
)

# Enable CORS for passenger mobile app and web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI & Vision Singletons
bay_manager = BayManager()
yolo_detector = YOLOBusDetector()
anpr_engine = ANPREngine()
live_camera = None

@app.on_event("startup")
def startup_event():
    # Sync bay polygons from DB on startup
    db = SessionLocal()
    try:
        bays = crud.get_bays(db)
        bay_manager.load_bays_from_db(bays)
        print(f"Loaded {len(bays)} bays into Spatial BayManager.")
    except Exception as e:
        print(f"Startup notice: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "system": "Smart Bus Stand Information System API",
        "status": "Online",
        "database": "PostgreSQL (smart_bus_db)",
        "modules": ["YOLOv11 Bus Detection", "ANPR License Recognition", "Rule-Based Bay Mapping"]
    }

# ==================== ROUTE ENDPOINTS ====================
@app.get("/routes/", response_model=List[schemas.Route])
def read_routes(db: Session = Depends(get_db)):
    return crud.get_routes(db)

@app.post("/routes/", response_model=schemas.Route)
def create_route(route: schemas.RouteCreate, db: Session = Depends(get_db)):
    return crud.create_route(db, route)

# ==================== BUS ENDPOINTS ====================
@app.get("/buses/", response_model=List[schemas.Bus])
def read_buses(db: Session = Depends(get_db)):
    return crud.get_buses(db)

@app.get("/buses/{registration_no}", response_model=schemas.Bus)
def read_bus(registration_no: str, db: Session = Depends(get_db)):
    bus = crud.get_bus_by_reg(db, registration_no)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus

@app.post("/buses/", response_model=schemas.Bus)
def create_bus(bus: schemas.BusCreate, db: Session = Depends(get_db)):
    return crud.create_bus(db, bus)

# ==================== PARKING BAY ENDPOINTS ====================
@app.get("/bays/", response_model=List[schemas.ParkingBay])
def read_bays(db: Session = Depends(get_db)):
    return crud.get_bays(db)

@app.post("/bays/", response_model=schemas.ParkingBay)
def create_bay(bay: schemas.ParkingBayCreate, db: Session = Depends(get_db)):
    return crud.create_bay(db, bay)

@app.put("/bays/{bay_id}/status", response_model=schemas.ParkingBay)
def update_bay(bay_id: str, status: str, vehicle_reg: Optional[str] = None, db: Session = Depends(get_db)):
    bay = crud.update_bay_status(db, bay_id, status, vehicle_reg)
    if not bay:
        raise HTTPException(status_code=404, detail="Bay not found")
    return bay

# ==================== DETECTION ENDPOINTS ====================
@app.post("/detections/", response_model=schemas.Detection)
def record_detection(detection: schemas.DetectionCreate, db: Session = Depends(get_db)):
    return crud.create_detection(db, detection)

@app.get("/detections/recent", response_model=List[schemas.Detection])
def read_recent_detections(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_recent_detections(db, limit)

# ==================== ANPR RECORD ENDPOINTS ====================
@app.get("/anpr/", response_model=List[schemas.ANPRRecord])
def read_anpr_records(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_anpr_records(db, limit)

@app.post("/anpr/", response_model=schemas.ANPRRecord)
def create_anpr_record(record: schemas.ANPRRecordCreate, db: Session = Depends(get_db)):
    return crud.create_anpr_record(db, record)

# ==================== SCHEDULE ENDPOINTS ====================
@app.get("/schedules/", response_model=List[schemas.Schedule])
def read_schedules(db: Session = Depends(get_db)):
    return crud.get_schedules(db)

@app.post("/schedules/", response_model=schemas.Schedule)
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    return crud.create_schedule(db, schedule)

# ==================== PASSENGER LIVE ADVISORY ====================
@app.get("/advisory/", response_model=List[schemas.AdvisoryItem])
def get_passenger_advisory(db: Session = Depends(get_db)):
    """Primary endpoint consumed by the passenger mobile application."""
    return crud.get_live_advisory(db)

# ==================== AI VISION PROCESSING ====================
@app.post("/vision/process_frame")
async def process_frame(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    End-to-End AI Pipeline:
    1. Read frame.
    2. YOLOv11 detects buses.
    3. Spatial rule-based engine identifies bay.
    4. ANPR recognizes license plate.
    5. Updates bay status and creates detection record in PostgreSQL.
    """
    import cv2
    import numpy as np

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # 1. Detect buses with YOLO
    buses = yolo_detector.detect_buses(frame)
    results = []

    for bus in buses:
        bbox = bus["bbox"]
        x1, y1, x2, y2 = bbox
        
        # 2. Rule-based parking bay identification
        assigned_bay = bay_manager.identify_bay(bbox)
        
        # 3. ANPR extraction on cropped bus/plate region
        cropped_bus = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
        anpr_result = anpr_engine.recognize_plate(cropped_bus)
        
        plate_no = anpr_result["plate_number"] if anpr_result else "UNKNOWN"
        conf = anpr_result["confidence"] if anpr_result else bus["confidence"] * 100.0

        # 4. Save detection & ANPR to PostgreSQL if a bay is identified
        if assigned_bay:
            # Confirm over multi-frame
            confirmed_bay = bay_manager.confirm_bay_assignment(plate_no, assigned_bay) or assigned_bay
            
            crud.create_detection(db, schemas.DetectionCreate(
                bus_registration=plate_no,
                bay_id=confirmed_bay,
                confidence=round(conf, 1)
            ))
            
            if plate_no != "UNKNOWN":
                crud.create_anpr_record(db, schemas.ANPRRecordCreate(
                    plate_number=plate_no,
                    camera_loc="CCTV-01",
                    confidence=conf,
                    match_status="Verified"
                ))

        results.append({
            "bbox": bbox,
            "assigned_bay": assigned_bay,
            "plate_number": plate_no,
            "confidence": conf
        })

    return {
        "buses_detected": len(buses),
        "results": results
    }

# ==================== LIVE VIDEO STREAMING ====================
def generate_mjpeg_stream():
    """Generator for multipart MJPEG video stream with live AI detection overlays."""
    import cv2
    import time

    global live_camera, yolo_detector, bay_manager
    while live_camera and live_camera.is_running:
        frame = live_camera.read_frame()
        if frame is None:
            time.sleep(0.04)
            continue

        # Run bus detection
        buses = yolo_detector.detect_buses(frame)
        bay_assignments = {}
        for idx, bus in enumerate(buses):
            bay = bay_manager.identify_bay(bus["bbox"])
            if bay:
                bay_assignments[idx] = bay

        annotated = yolo_detector.draw_detections(frame, buses, bay_assignments)
        ret, buffer = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.033) # ~30 FPS

@app.get("/vision/video_feed")
def video_feed():
    """MJPEG streaming endpoint for CCTV camera stream with real-time AI bounding boxes."""
    global live_camera
    if live_camera is None or not live_camera.is_running:
        raise HTTPException(status_code=503, detail="Camera feed is not active. Start camera via /vision/camera/start")
    return StreamingResponse(generate_mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/vision/camera/start")
def start_camera(source: str = "0"):
    """Starts video camera streamer with specified device ID, RTSP URL, or video path."""
    global live_camera
    if live_camera and live_camera.is_running:
        live_camera.stop()
    src = int(source) if source.isdigit() else source
    live_camera = VideoCamera(source=src)
    return {"status": "Camera started", "source": source}

@app.post("/vision/camera/stop")
def stop_camera():
    """Stops the active video camera streamer."""
    global live_camera
    if live_camera:
        live_camera.stop()
        live_camera = None
    return {"status": "Camera stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

