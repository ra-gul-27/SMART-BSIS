from app.db.database import get_connection

class DashboardModel:
    @staticmethod
    def get_kpis():
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total Buses
        cursor.execute("SELECT COUNT(*) FROM buses")
        total_buses = cursor.fetchone()[0]
        
        # Active Routes
        cursor.execute("SELECT COUNT(*) FROM routes WHERE status = 'Active'")
        active_routes = cursor.fetchone()[0]
        
        # Parking Bays
        cursor.execute("SELECT COUNT(*) FROM parking_bays")
        total_bays = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parking_bays WHERE status = 'Available'")
        available_bays = cursor.fetchone()[0]
        
        # In Terminal (Occupied bays + some buffer if needed)
        in_terminal = total_bays - available_bays
        
        # Alerts
        cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'error'")
        active_alerts = cursor.fetchone()[0]
        
        # Live Detected (Mocked dynamically for now)
        live_detected = 48
        
        conn.close()
        
        return [
            {"title": "Total\nBuses", "value": str(total_buses), "sub": "+12\ntoday", "alert": False, "icon": "🚍", "sub_bg": True},
            {"title": "Live\nDetected", "value": str(live_detected), "sub": "Active AI", "alert": False, "icon": "📹", "sub_bg": False},
            {"title": "Active\nRoutes", "value": str(active_routes), "sub": None, "alert": False, "icon": "⛕", "sub_bg": False},
            {"title": "Active\nAlerts", "value": str(active_alerts), "sub": None, "alert": True if active_alerts > 0 else False, "icon": "⚠", "sub_bg": False},
            {"title": "Parking\nBays", "value": str(total_bays), "sub": f"{available_bays} available", "alert": False, "icon": "P", "sub_bg": False},
            {"title": "In\nTerminal", "value": str(in_terminal), "sub": None, "alert": False, "icon": "🏢", "sub_bg": False},
        ]

    @staticmethod
    def get_parking_bays():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT bay_id, status, vehicle_reg FROM parking_bays ORDER BY bay_id")
        bays = []
        for row in cursor.fetchall():
            bays.append({
                "id": row[0],
                "status": row[1],
                "vehicle": row[2]
            })
        conn.close()
        return bays

    @staticmethod
    def get_events(limit=5):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, title, description, event_type FROM events ORDER BY timestamp DESC LIMIT %s", (limit,))
        events = []
        for row in cursor.fetchall():
            # Format time for UI: just HH:MM:SS
            time_str = str(row[0]).split(" ")[1] if " " in str(row[0]) else str(row[0])
            is_alert = row[3] == "error"
            # Map color based on type
            color = "#ef4444" if is_alert else ("#3b82f6" if row[3] == "primary" else "#10b981")
            
            events.append((time_str, row[1], row[2], color, is_alert))
        conn.close()
        return events
