from app.db.database import get_connection

class ParkingBayModel:
    @staticmethod
    def get_all_bays():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT bay_id, status, vehicle_reg FROM parking_bays ORDER BY bay_id")
        bays = []
        for row in cursor.fetchall():
            bays.append({
                "bay_id": row[0],
                "status": row[1],
                "vehicle_reg": row[2]
            })
        conn.close()
        return bays
