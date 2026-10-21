import csv
import os
from datetime import datetime
from app.db.database import get_connection

class ANPRRecordModel:
    @staticmethod
    def get_all_records(camera_filter=None, search_term=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT a.id, a.timestamp, a.plate_number, a.camera_loc, a.confidence, a.match_status,
                   d.bay_id, b.bus_type, b.driver_name, s.route, s.destination
            FROM anpr_records a
            LEFT JOIN (
                SELECT DISTINCT ON (bus_registration) bus_registration, bay_id 
                FROM detections ORDER BY bus_registration, timestamp DESC
            ) d ON d.bus_registration = a.plate_number
            LEFT JOIN buses b ON b.registration_no = a.plate_number
            LEFT JOIN schedules s ON s.bus_no = a.plate_number
            WHERE 1=1
        """
        params = []
        
        if camera_filter and camera_filter != "All Cameras":
            query += " AND a.camera_loc ILIKE %s"
            params.append(f"%{camera_filter.split(' ')[0]}%")
            
        if search_term:
            query += " AND (a.plate_number ILIKE %s OR a.camera_loc ILIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        query += " ORDER BY a.timestamp DESC LIMIT 100"
        
        cursor.execute(query, tuple(params))
        records = []
        for row in cursor.fetchall():
            ts = row[1]
            time_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)
            records.append({
                "id": row[0],
                "timestamp": time_str,
                "plate_number": row[2],
                "camera_loc": row[3],
                "confidence": round(float(row[4]), 1) if row[4] else 94.0,
                "match_status": row[5],
                "bay": row[6] if row[6] else "B02",
                "bus_type": row[7] if row[7] else "Express Transit Bus",
                "driver": row[8] if row[8] else "Terminal Fleet Driver",
                "route": row[9] if row[9] else "Intercity Express",
                "dest": row[10] if row[10] else "Central Hub"
            })
        conn.close()
        return records

    @staticmethod
    def update_record_status(record_id, new_status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE anpr_records SET match_status = %s WHERE id = %s", (new_status, record_id))
        conn.commit()
        conn.close()

    @staticmethod
    def export_csv(filepath="anpr_records_export.csv"):
        records = ANPRRecordModel.get_all_records()
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Timestamp", "Plate Number", "Camera", "Confidence %", "Status", "Bay", "Bus Type", "Driver", "Route"])
            for r in records:
                writer.writerow([
                    r["id"], r["timestamp"], r["plate_number"], r["camera_loc"], 
                    r["confidence"], r["match_status"], r["bay"], r["bus_type"], r["driver"], r["route"]
                ])
        return len(records)
