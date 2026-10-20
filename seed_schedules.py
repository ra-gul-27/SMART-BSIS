import psycopg2
from app.constants import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY, 
    bus_no VARCHAR NOT NULL, 
    route VARCHAR NOT NULL, 
    destination VARCHAR NOT NULL, 
    bay VARCHAR NOT NULL, 
    departure_time VARCHAR NOT NULL, 
    arrival_time VARCHAR NOT NULL, 
    fare VARCHAR NOT NULL, 
    status VARCHAR NOT NULL
)''')

cur.execute('SELECT COUNT(*) FROM schedules')
count = cur.fetchone()[0]
print('Count:', count)

if count == 0:
    schedules = [
        ("NY-102", "Exp. Central", "to Downtown", "A1", "08:15 AM", "09:30 AM", "$4.50", "BOARDING"), 
        ("BS-405", "Local North", "to Highland Park", "B3", "08:30 AM", "09:45 AM", "$2.50", "SCHEDULED"), 
        ("CH-882", "Intercity", "to Metro West", "A4", "08:00 AM", "--", "$6.00", "DELAYED (15m)"), 
        ("NY-101", "Exp. Central", "to Downtown", "A1", "07:45 AM", "09:00 AM", "$4.50", "DEPARTED")
    ]
    cur.executemany("INSERT INTO schedules (bus_no, route, destination, bay, departure_time, arrival_time, fare, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", schedules)

conn.commit()
print('Done')
conn.close()
