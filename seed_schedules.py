import psycopg2
from app.constants import DB_CONFIG

def seed_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 1. Real Bus Master Data
    buses = [
        ('TN 01 AN 2345', 'AC Volvo Express', 45, 'Active', 'Kannan P', '2026-10-15'),
        ('TN 38 N 4567', 'Deluxe Air-Suspension', 48, 'Active', 'M. Selvan', '2026-10-18'),
        ('TN 01 AB 1234', 'AC Semi-Sleeper', 45, 'Active', 'Rajesh Kumar', '2026-10-10'),
        ('TN 02 XY 9876', 'Super Fast Seater', 55, 'Active', 'Suresh M', '2026-10-12'),
        ('TN 05 XY 7788', 'Classic Sleeper', 36, 'Active', 'Murugan S', '2026-10-08'),
        ('TN 43 B 1284', 'Ultra Deluxe', 50, 'Active', 'V. Anand', '2026-10-14')
    ]

    for reg, btype, cap, st, drv, maint in buses:
        cur.execute('''
            INSERT INTO buses (registration_no, bus_type, capacity, status, driver_name, last_maintenance)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (registration_no) DO UPDATE 
            SET bus_type = EXCLUDED.bus_type,
                capacity = EXCLUDED.capacity,
                status = EXCLUDED.status,
                driver_name = EXCLUDED.driver_name,
                last_maintenance = EXCLUDED.last_maintenance;
        ''', (reg, btype, cap, st, drv, maint))

    cur.execute("DELETE FROM buses WHERE registration_no = 'tn 0807';")

    # 2. Real Routes Master Data
    routes = [
        ('R-01', 'Chennai Central', 'Bangalore Shantinagar', 'Vellore, Ambur, Hosur', 350.0, 360, 'Active'),
        ('R-02', 'Chennai Central', 'Coimbatore Gandhipuram', 'Salem, Erode, Tiruppur', 510.0, 480, 'Active'),
        ('R-03', 'Chennai Central', 'Madurai Mattuthavani', 'Villupuram, Trichy, Dindigul', 460.0, 450, 'Active'),
        ('R-04', 'Chennai Central', 'Pondicherry Bus Stand', 'Mahabalipuram, Marakkanam', 160.0, 180, 'Active'),
        ('R-05', 'Chennai Central', 'Salem New Bus Stand', 'Ulundurpet, Kallakurichi', 340.0, 330, 'Active')
    ]

    for rid, src, dst, via, dist, dur, st in routes:
        cur.execute('''
            INSERT INTO routes (route_id, source, destination, via_stops, distance_km, duration_mins, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (route_id) DO UPDATE 
            SET source = EXCLUDED.source,
                destination = EXCLUDED.destination,
                via_stops = EXCLUDED.via_stops,
                distance_km = EXCLUDED.distance_km,
                duration_mins = EXCLUDED.duration_mins,
                status = EXCLUDED.status;
        ''', (rid, src, dst, via, dist, dur, st))

    cur.execute("DELETE FROM routes WHERE route_id = 'R77';")

    # 3. Synchronized Schedules Master Data
    cur.execute('TRUNCATE TABLE schedules RESTART IDENTITY;')
    schedules = [
        ('TN 01 AN 2345', 'R-01 (Chennai - Bangalore)', 'Bangalore Shantinagar', 'B02', '11:45 AM', '05:45 PM', 'Rs 650.00', 'BOARDING'),
        ('TN 38 N 4567', 'R-02 (Chennai - Coimbatore)', 'Coimbatore Gandhipuram', 'B03', '12:30 PM', '08:30 PM', 'Rs 720.00', 'SCHEDULED'),
        ('TN 01 AB 1234', 'R-03 (Chennai - Madurai)', 'Madurai Mattuthavani', 'B01', '01:15 PM', '08:45 PM', 'Rs 580.00', 'SCHEDULED'),
        ('TN 02 XY 9876', 'R-04 (Chennai - Pondicherry)', 'Pondicherry Bus Stand', 'B04', '02:00 PM', '05:00 PM', 'Rs 220.00', 'SCHEDULED'),
        ('TN 05 XY 7788', 'R-05 (Chennai - Salem)', 'Salem New Bus Stand', 'B05', '02:45 PM', '08:15 PM', 'Rs 450.00', 'SCHEDULED'),
        ('TN 43 B 1284', 'R-01 (Chennai - Bangalore)', 'Bangalore Shantinagar', 'B06', '03:30 PM', '09:30 PM', 'Rs 650.00', 'SCHEDULED')
    ]
    cur.executemany('''
        INSERT INTO schedules (bus_no, route, destination, bay, departure_time, arrival_time, fare, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', schedules)

    # 4. Synchronized Terminal Parking Bays
    cur.execute("UPDATE parking_bays SET status = 'Occupied', vehicle_reg = 'TN 01 AN 2345' WHERE bay_id = 'B02';")
    cur.execute("UPDATE parking_bays SET status = 'Occupied', vehicle_reg = 'TN 38 N 4567' WHERE bay_id = 'B03';")
    cur.execute("UPDATE parking_bays SET status = 'Available', vehicle_reg = NULL WHERE bay_id NOT IN ('B02', 'B03');")

    conn.commit()
    print('[SUCCESS] Successfully synchronized and enriched all database tables with real bus manifest data!')
    conn.close()

if __name__ == '__main__':
    seed_database()
