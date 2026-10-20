import os
from typing import List, Dict, Any, Tuple, Optional

class YOLOBusDetector:
    """
    YOLOv11 Real-Time Bus Detector for Bus Terminal CCTV Streams.
    Detects buses, extracts bounding boxes, confidences, and spatial anchor points.
    """
    def __init__(self, model_name: str = "yolo11n.pt", conf_thresh: float = 0.45):
        self.model_name = model_name
        self.conf_thresh = conf_thresh
        self.model = None
        self._init_model()

    def _init_model(self):
        try:
            from ultralytics import YOLO
            # Ultralytics will auto-download yolo11n.pt on first load if not present
            self.model = YOLO(self.model_name)
            print(f"[SUCCESS] YOLO Bus Detector initialized with model: {self.model_name}")
        except Exception as e:
            print(f"[INFO] YOLO initialization notice: {e}. Running in simulation/fallback mode.")
            self.model = None

    def detect_buses(self, frame) -> List[Dict[str, Any]]:
        """
        Run inference on an OpenCV frame (numpy ndarray).
        Returns filtered list of bus detections.
        """
        if self.model is None:
            # Fallback mock detection for development if model is loading
            return []

        detections = []
        try:
            # Class 5 = bus, Class 7 = truck in standard COCO dataset
            results = self.model(frame, conf=self.conf_thresh, classes=[5, 7], verbose=False)
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names.get(cls_id, "bus")
                    
                    bottom_center = ((x1 + x2) / 2.0, y2)
                    centroid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
                    
                    detections.append({
                        "bbox": (int(x1), int(y1), int(x2), int(y2)),
                        "confidence": round(conf, 3),
                        "class_name": cls_name,
                        "bottom_center": (int(bottom_center[0]), int(bottom_center[1])),
                        "centroid": (int(centroid[0]), int(centroid[1]))
                    })
        except Exception as e:
            print(f"Error during YOLO detection: {e}")

        return detections

    def draw_detections(self, frame, detections: List[Dict[str, Any]], bay_assignments: Optional[Dict[int, str]] = None):
        """
        Annotates OpenCV frame with bounding boxes, labels, and bay assignments.
        """
        import cv2
        annotated = frame.copy()
        for idx, det in enumerate(detections):
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            
            bay_label = f" | Bay: {bay_assignments[idx]}" if bay_assignments and idx in bay_assignments else ""
            label = f"BUS {int(conf * 100)}%{bay_label}"
            
            # Green / Blue bounding box
            color = (33, 112, 228) # BGR: bright blue
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Label banner
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(annotated, (x1, y1 - 22), (x1 + w + 8, y1), color, -1)
            cv2.putText(annotated, label, (x1 + 4, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            
            # Draw bottom-center contact dot
            bx, by = det["bottom_center"]
            cv2.circle(annotated, (bx, by), 5, (0, 255, 0), -1)

        return annotated
