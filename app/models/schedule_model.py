from app.db.database import get_connection

class ScheduleModel:
    @staticmethod
    def get_all_schedules(route_filter=None, bay_filter=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, bus_no, route, destination, bay, departure_time, arrival_time, fare, status FROM schedules WHERE 1=1"
        params = []
        
        if route_filter:
            query += " AND (route ILIKE %s OR destination ILIKE %s)"
            params.extend([f"%{route_filter}%", f"%{route_filter}%"])
        if bay_filter:
            query += " AND bay ILIKE %s"
            params.append(f"%{bay_filter}%")
            
        query += " ORDER BY id"
        cursor.execute(query, tuple(params))
        
        schedules = []
        for row in cursor.fetchall():
            schedules.append({
                "id": row[0],
                "bus": row[1],
                "route": row[2],
                "dest": row[3],
                "bay": row[4],
                "dep": row[5],
                "arr": row[6],
                "fare": row[7],
                "status": row[8]
            })
        conn.close()
        return schedules

    @staticmethod
    def add_schedule(bus, route, dest, bay, dep, arr, fare, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO schedules (bus_no, route, destination, bay, departure_time, arrival_time, fare, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (bus, route, dest, bay, dep, arr, fare, status))
        conn.commit()
        conn.close()

    @staticmethod
    def update_schedule_status(sched_id, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE schedules SET status = %s WHERE id = %s", (status, sched_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_schedule(sched_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schedules WHERE id = %s", (sched_id,))
        conn.commit()
        conn.close()
