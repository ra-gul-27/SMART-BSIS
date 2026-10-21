from app.db.database import get_connection

class RouteModel:
    @staticmethod
    def get_all_routes():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT route_id, source, destination, via_stops, distance_km, duration_mins, status FROM routes ORDER BY route_id")
        routes = []
        for row in cursor.fetchall():
            routes.append({
                "route_id": row[0],
                "source": row[1],
                "destination": row[2],
                "via_stops": row[3],
                "distance": f"{row[4]} km",
                "duration": f"{row[5]} mins",
                "status": row[6]
            })
        conn.close()
        return routes

    @staticmethod
    def add_route(route_id, source, destination, via_stops, distance, duration, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO routes (route_id, source, destination, via_stops, distance_km, duration_mins, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (route_id) DO UPDATE
        SET source = EXCLUDED.source,
            destination = EXCLUDED.destination,
            via_stops = EXCLUDED.via_stops,
            distance_km = EXCLUDED.distance_km,
            duration_mins = EXCLUDED.duration_mins,
            status = EXCLUDED.status;
        ''', (route_id, source, destination, via_stops, distance, duration, status))
        conn.commit()
        conn.close()

    @staticmethod
    def toggle_route_status(route_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM routes WHERE route_id = %s", (route_id,))
        row = cursor.fetchone()
        if row:
            new_st = "Suspended" if row[0] == "Active" else "Active"
            cursor.execute("UPDATE routes SET status = %s WHERE route_id = %s", (new_st, route_id))
            conn.commit()
        conn.close()
