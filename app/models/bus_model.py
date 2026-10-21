from app.db.database import get_connection

class BusModel:
    @staticmethod
    def get_all_buses(search_term=None, status_filter=None):
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT registration_no, bus_type, capacity, status, driver_name, last_maintenance FROM buses WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (registration_no ILIKE %s OR bus_type ILIKE %s OR driver_name ILIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
            
        if status_filter and status_filter != "All Status":
            query += " AND status ILIKE %s"
            params.append(f"%{status_filter}%")
            
        query += " ORDER BY registration_no"
        cursor.execute(query, tuple(params))
        
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
        ON CONFLICT (registration_no) DO UPDATE
        SET bus_type = EXCLUDED.bus_type,
            capacity = EXCLUDED.capacity,
            status = EXCLUDED.status,
            driver_name = EXCLUDED.driver_name,
            last_maintenance = EXCLUDED.last_maintenance;
        ''', (reg, b_type, capacity, status, driver, maintenance))
        conn.commit()
        conn.close()

    @staticmethod
    def toggle_bus_status(reg):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM buses WHERE registration_no = %s", (reg,))
        row = cursor.fetchone()
        if row:
            current_status = row[0]
            new_status = "Maintenance" if current_status == "Active" else "Active"
            cursor.execute("UPDATE buses SET status = %s WHERE registration_no = %s", (new_status, reg))
            conn.commit()
        conn.close()
