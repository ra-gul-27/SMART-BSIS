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

    @staticmethod
    def update_bay_status(bay_id, status, vehicle_reg=None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE parking_bays SET status = %s, vehicle_reg = %s WHERE bay_id = %s", (status, vehicle_reg, bay_id))
        conn.commit()
        conn.close()

    @staticmethod
    def release_bay(bay_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE parking_bays SET status = 'Available', vehicle_reg = NULL WHERE bay_id = %s", (bay_id,))
        conn.commit()
        conn.close()
