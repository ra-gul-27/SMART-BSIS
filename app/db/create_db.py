import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.constants import DB_CONFIG

def ensure_database_exists():
    # Connect to the default 'postgres' database to create the new DB
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database="postgres",
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_CONFIG['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Database {DB_CONFIG['database']} does not exist. Creating...")
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"Database {DB_CONFIG['database']} created successfully.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")

if __name__ == "__main__":
    ensure_database_exists()
