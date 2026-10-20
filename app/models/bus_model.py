from app.db.database import get_connection

class BusModel:
    @staticmethod
    def get_all_buses():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT registration_no, bus_type, capacity, status, driver_name, last_maintenance FROM buses ORDER BY registration_no")
        buses = []
        for row in cursor.fetchall():
            buses.append({
                "reg": row[0],
                "type": row[1],
                "capacity": str(row[2]),
                "status": row[3],
                "driver": row[4],
                "last_maintenance": str(row[5]) if row[5] else "-"
            })
        conn.close()
        return buses

    @staticmethod
    def add_bus(reg, b_type, capacity, status, driver, maintenance):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO buses (registration_no, bus_type, capacity, status, driver_name, last_maintenance)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', (reg, b_type, capacity, status, driver, maintenance))
        conn.commit()
        conn.close()
