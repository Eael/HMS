from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from . import models


# Create all database tables
# This will create the tables defined in the models if they do not exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Hotel Management System API",
    description="API for managing hotel operations including user management, room bookings, and more.",
    version="1.0.0"
)

# Root endpoint
@app.get("/", tags=["Home"])
async def read_root():
    return {"message": "Welcome to the Hotel Management System API!"}