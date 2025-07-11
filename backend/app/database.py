from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is used for SQLite to allow multiple threads to use the same connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create a configured "Session" class
# Each instance of SessionLocal will be a new database session
# SessionLocal is a factory for new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
# This is the base class for all models that will be defined in the application
Base = declarative_base()

# Dependency to get the database session
# This function will be used in FastAPI routes to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
