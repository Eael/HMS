from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional, List
from datetime import timedelta
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from . import models, schemas, auth, crud


# Create all database tables
# This will create the tables defined in the models if they do not exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Hotel Management System API",
    description="API for managing hotel operations including user management, room bookings, and more.",
    version="1.0.1",
    # docs_url="/docs",  # Uncomment to change the docs URL
    # redoc_url="/redoc",  # Uncomment to change the ReDoc URL
    # Add CORS middleware if needed
    # cors_origins=["*"],  # Uncomment to allow all origins, or specify allowed origins

)

# Root endpoint
@app.get("/", tags=["Home"])
async def read_root():
    return {"message": "Welcome to the Hotel Management System API!"}


# --- User Authentication and Management Endpoints ---
@app.post("/token", response_model=schemas.Token, tags=["Authentication"])  
async def login(
    form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
    ):
    """Authenticate user and return access token on successful login."""
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, tags=["User Management"])
async def create_user(
    user: schemas.UserCreate, db: Session = Depends(get_db)
    ):
    """Create a new user."""
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    existing_email = crud.get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.create_user(db=db, user=user)


@app.get("/users/me", response_model=schemas.User, tags=["User Management"])
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)
    ):
    """Get the current authenticated user."""
    return current_user


# --- User Management Endpoints (Admin Only) ---

@app.get("/users/", response_model=List[schemas.User], tags=["User Management"])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    is_admin: bool = Depends(auth.check_user_role),
    ):
    """Get a list of users with pagination. Admin only."""
    if not is_admin:
        # If the user is not an admin, raise a 403 Forbidden error
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return crud.get_users(db=db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User, tags=["User Management"])
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    is_admin: bool = Depends(auth.check_user_role),
    ):
    """Get a user by ID. Admin only."""
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.put("/users/{user_id}", response_model=schemas.User, tags=["User Management"])
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    is_admin: bool = Depends(auth.check_user_role),
    ):
    """Update an existing user. Admin only."""
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    
    updated_user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@app.delete("/users/{user_id}", response_model=schemas.User, tags=["User Management"])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    is_admin: bool = Depends(auth.check_user_role),
    ):
    """Delete a user by ID. Admin only."""
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    
    deleted_user = crud.delete_user(db=db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return deleted_user

# --- Include other routers or endpoints as needed ---
