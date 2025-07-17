from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas
from .auth import hash_password, verify_password


# --- User CRUD operations ---
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """Get a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_password = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number if user.phone_number else None,
        address=user.address if user.address else None,
        role=user.role, # Default role is 'guest'
        hashed_password=hashed_password
    )
    db.add(db_user) # Add the new user to the session
    db.commit() # Commit the session to save the user
    db.refresh(db_user) # Refresh the instance to get the updated data
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update an existing user."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    # Update fields if provided
    if user_update.username:
        db_user.username = user_update.username
    if user_update.email:
        db_user.email = user_update.email
    if user_update.first_name:
        db_user.first_name = user_update.first_name
    if user_update.last_name:
        db_user.last_name = user_update.last_name
    if user_update.phone_number:
        db_user.phone_number = user_update.phone_number
    if user_update.address:
        db_user.address = user_update.address
    if user_update.role:
        db_user.role = user_update.role
    if user_update.password:
        db_user.hashed_password = hash_password(user_update.password)

    db.commit() # Commit the session to save changes
    db.refresh(db_user) # Refresh the instance to get the updated data
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    """Delete a user by ID."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    db.delete(db_user) # Delete the user from the session
    db.commit() # Commit the session to save changes
    return db_user