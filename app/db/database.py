import psycopg2
from app.constants import DB_CONFIG
from datetime import datetime, timedelta

def get_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Create Buses Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id SERIAL PRIMARY KEY,
            registration_no VARCHAR UNIQUE NOT NULL,
            bus_type VARCHAR NOT NULL,
            capacity INTEGER NOT NULL,
            status VARCHAR NOT NULL,
            driver_name VARCHAR,
            last_maintenance DATE
        )
        ''')

        # Create Routes Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id SERIAL PRIMARY KEY,
            route_id VARCHAR UNIQUE NOT NULL,
            source VARCHAR NOT NULL,
            destination VARCHAR NOT NULL,
            via_stops VARCHAR,
            distance_km REAL,
            duration_mins INTEGER,
            status VARCHAR NOT NULL
        )
        ''')

        # Create Parking Bays Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_bays (
            id SERIAL PRIMARY KEY,
            bay_id VARCHAR UNIQUE NOT NULL,
            status VARCHAR NOT NULL,
            vehicle_reg VARCHAR
        )
        ''')

        # Create Events Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            title VARCHAR NOT NULL,
            description TEXT,
            event_type VARCHAR NOT NULL
        )
        ''')

        # Create ANPR Records Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS anpr_records (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            plate_number VARCHAR NOT NULL,
            camera_loc VARCHAR NOT NULL,
            confidence REAL NOT NULL,
            match_status VARCHAR NOT NULL
        )
        ''')

        # Create Schedules Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id SERIAL PRIMARY KEY,
            bus_no VARCHAR NOT NULL,
            route VARCHAR NOT NULL,
            destination VARCHAR NOT NULL,
            bay VARCHAR NOT NULL,
            departure_time VARCHAR NOT NULL,
            arrival_time VARCHAR NOT NULL,
            fare VARCHAR NOT NULL,
            status VARCHAR NOT NULL
        )
        ''')

        conn.commit()
        
        # Check if we need to seed data
        cursor.execute("SELECT COUNT(*) FROM parking_bays")
        if cursor.fetchone()[0] == 0:
            seed_database(conn)
            
        conn.close()
    except Exception as e:
        print(f"PostgreSQL Database Initialization Error: {e}")
        # Note: If database doesn't exist, this will fail. User needs to create it.

def seed_database(conn):
    cursor = conn.cursor()
    
    # Seed Bays
    bays = [
        ("B01", "Occupied", "TN 01 AB 1234"),
        ("B02", "Available", None),
        ("B03", "Occupied", "TN 02 XY 9876"),
        ("B04", "Available", None),
        ("B05", "Available", None),
        ("B06", "Occupied", "TN 01 AN 2345"),
        ("B07", "Available", None),
        ("B08", "Available", None)
    ]
    cursor.executemany("INSERT INTO parking_bays (bay_id, status, vehicle_reg) VALUES (%s, %s, %s)", bays)

    # Seed Events
    now = datetime.now()
    events = [
        ((now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"), "BUS DETECTED", "TN 01 AN 2345, Bay 12", "primary"),
        ((now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"), "ANPR", "TN 01 AP 1284, 96% Match", "secondary"),
        ((now - timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"), "⚠ ALERT", "Camera 04 offline in Zone B", "error"),
        ((now - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"), "BUS DEPARTED", "TN 05 XY 7788, Bay 02", "primary"),
    ]
    cursor.executemany("INSERT INTO events (timestamp, title, description, event_type) VALUES (%s, %s, %s, %s)", events)

    # Seed ANPR Records
    anpr = [
        (now - timedelta(minutes=5), "TN 01 AB 1234", "CAM-01 (Entry)", 98.5, "Verified"),
        (now - timedelta(minutes=15), "KL 07 CD 5678", "CAM-02 (Exit)", 95.2, "Verified"),
        (now - timedelta(minutes=45), "UNKNOWN", "CAM-01 (Entry)", 42.1, "Unverified"),
        (now - timedelta(minutes=65), "MH 12 EF 9012", "CAM-03 (Bay A)", 99.1, "Verified")
    ]
    cursor.executemany("INSERT INTO anpr_records (timestamp, plate_number, camera_loc, confidence, match_status) VALUES (%s, %s, %s, %s, %s)", anpr)

    # Seed Schedules
    schedules = [
        ("NY-102", "Exp. Central", "to Downtown", "A1", "08:15 AM", "09:30 AM", "$4.50", "BOARDING"),
        ("BS-405", "Local North", "to Highland Park", "B3", "08:30 AM", "09:45 AM", "$2.50", "SCHEDULED"),
        ("CH-882", "Intercity", "to Metro West", "A4", "08:00 AM", "--", "$6.00", "DELAYED (15m)"),
        ("NY-101", "Exp. Central", "to Downtown", "A1", "07:45 AM", "09:00 AM", "$4.50", "DEPARTED")
    ]
    cursor.executemany("INSERT INTO schedules (bus_no, route, destination, bay, departure_time, arrival_time, fare, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", schedules)

    # Seed Buses
    buses = [
        ("TN 01 AB 1234", "AC Semi-Sleeper", 45, "Active", "Rajesh Kumar", "2024-01-15"),
        ("TN 02 XY 9876", "Non-AC Seater", 55, "Active", "Suresh M", "2024-02-10"),
        ("TN 01 AN 2345", "AC Volvo", 40, "Maintenance", "Kannan P", "2024-03-01"),
        ("TN 05 XY 7788", "Non-AC Sleeper", 30, "Active", "Murugan", "2024-02-28")
    ]
    cursor.executemany("INSERT INTO buses (registration_no, bus_type, capacity, status, driver_name, last_maintenance) VALUES (%s, %s, %s, %s, %s, %s)", buses)

    # Seed Routes
    routes = [
        ("R-01", "Chennai", "Bangalore", "Vellore, Krishnagiri", 350.5, 360, "Active"),
        ("R-02", "Chennai", "Coimbatore", "Villupuram, Salem", 500.0, 480, "Active"),
        ("R-03", "Chennai", "Madurai", "Trichy", 460.0, 420, "Suspended")
    ]
    cursor.executemany("INSERT INTO routes (route_id, source, destination, via_stops, distance_km, duration_mins, status) VALUES (%s, %s, %s, %s, %s, %s, %s)", routes)

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
