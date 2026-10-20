import json
from typing import List, Tuple, Optional, Dict

class BayManager:
    """
    Rule-Based Spatial Bay Identification Engine.
    Uses point-in-polygon geometric testing to map bus detections to terminal parking bays.
    """
    def __init__(self, bay_polygons: Optional[Dict[str, List[List[int]]]] = None):
        # Default bay polygon layout for terminal (normalized or pixel coords)
        # 8 bays arranged in 2 rows of 4 (camera frame 1280x720)
        self.bays = bay_polygons or {
            "B01": [[50, 100], [320, 100], [320, 380], [50, 380]],
            "B02": [[350, 100], [620, 100], [620, 380], [350, 380]],
            "B03": [[650, 100], [920, 100], [920, 380], [650, 380]],
            "B04": [[950, 100], [1220, 100], [1220, 380], [950, 380]],
            "B05": [[50, 420], [320, 420], [320, 700], [50, 700]],
            "B06": [[350, 420], [620, 420], [620, 700], [350, 700]],
            "B07": [[650, 420], [920, 420], [920, 700], [650, 700]],
            "B08": [[950, 420], [1220, 420], [1220, 700], [950, 700]],
        }
        # Multi-frame confirmation tracking: {bus_reg: (current_bay_candidate, count)}
        self.frame_history = {}
        self.required_confirmations = 3

    def set_bay_polygon(self, bay_id: str, polygon: List[List[int]]):
        """Configure or update the polygon boundary for a bay."""
        self.bays[bay_id] = polygon

    def load_bays_from_db(self, db_bays: list):
        """Load polygon coordinates from database parking_bays rows."""
        for bay in db_bays:
            if hasattr(bay, "polygon_points") and bay.polygon_points:
                try:
                    poly = json.loads(bay.polygon_points)
                    self.bays[bay.bay_id] = poly
                except Exception:
                    pass

    @staticmethod
    def is_point_in_polygon(point: Tuple[float, float], polygon: List[List[int]]) -> bool:
        """
        Ray-Casting Algorithm for Point-in-Polygon test.
        Returns True if the point (x, y) is inside the polygon.
        """
        x, y = point
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def identify_bay(self, bbox: Tuple[float, float, float, float]) -> Optional[str]:
        """
        Given a bus bounding box (x1, y1, x2, y2), calculates the bottom-center point
        (where the bus wheels contact the pavement) and matches it to a designated bay.
        """
        x1, y1, x2, y2 = bbox
        bottom_center = ((x1 + x2) / 2.0, y2)
        centroid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

        # First test bottom-center (standard ground-plane anchor)
        for bay_id, polygon in self.bays.items():
            if self.is_point_in_polygon(bottom_center, polygon):
                return bay_id

        # Fallback to centroid test
        for bay_id, polygon in self.bays.items():
            if self.is_point_in_polygon(centroid, polygon):
                return bay_id

        return None

    def confirm_bay_assignment(self, bus_id: str, detected_bay: Optional[str]) -> Optional[str]:
        """
        Multi-frame confirmation: A bus must be detected in the same bay
        for at least `required_confirmations` consecutive frames to prevent false flips.
        """
        if not detected_bay:
            self.frame_history.pop(bus_id, None)
            return None

        if bus_id not in self.frame_history:
            self.frame_history[bus_id] = (detected_bay, 1)
            return None

        candidate_bay, count = self.frame_history[bus_id]
        if candidate_bay == detected_bay:
            new_count = count + 1
            self.frame_history[bus_id] = (candidate_bay, new_count)
            if new_count >= self.required_confirmations:
                return candidate_bay
        else:
            self.frame_history[bus_id] = (detected_bay, 1)

        return None
