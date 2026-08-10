import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

# Resolve the database URL
database_url = settings.DATABASE_URL

# Render (and some other cloud providers) supply the legacy "postgres://" scheme.
# SQLAlchemy 2.x only accepts "postgresql://", so we fix it here.
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# For local SQLite development: create the database folder if it doesn't exist
if database_url.startswith("sqlite:///"):
    db_path = database_url.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        db_path = os.path.join(root_dir, db_path)
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# SQLite requires check_same_thread=False for multi-threaded FastAPI usage
connect_args = {}
if database_url.startswith("sqlite:///"):
    connect_args = {"check_same_thread": False}

engine = create_engine(database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
