from app.db.database import get_connection

class ScheduleModel:
    @staticmethod
    def get_all_schedules():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, bus_no, route, destination, bay, departure_time, arrival_time, fare, status FROM schedules ORDER BY id")
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
