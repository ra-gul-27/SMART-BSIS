from app.db.database import get_connection

class ANPRRecordModel:
    @staticmethod
    def get_all_records():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, plate_number, camera_loc, confidence, match_status FROM anpr_records ORDER BY timestamp DESC")
        records = []
        for row in cursor.fetchall():
            records.append({
                "timestamp": str(row[0].strftime("%Y-%m-%d %H:%M:%S")),
                "plate_number": row[1],
                "camera_loc": row[2],
                "confidence": row[3],
                "match_status": row[4]
            })
        conn.close()
        return records
