import os
import sys
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Add root directory to path to access app.constants
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.constants import DB_CONFIG

# URL-encode password in case it contains special characters like '@'
encoded_password = urllib.parse.quote_plus(DB_CONFIG["password"])

# Connect to PostgreSQL using psycopg2 dialect (smart_bus_db)
POSTGRES_URL = (
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{encoded_password}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

try:
    engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
    # Test connection
    with engine.connect() as test_conn:
        pass
    print("[SUCCESS] FastAPI Backend connected directly to PostgreSQL (smart_bus_db)")
except Exception as e:
    print(f"[WARNING] Could not connect to PostgreSQL ({e}). Falling back to SQLite.")
    SQLITE_URL = "sqlite:///./bus_stand.db"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
