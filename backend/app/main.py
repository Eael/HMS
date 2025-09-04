from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from decimal import Decimal

from .database import engine, Base, get_db
from . import models, schemas, crud, auth

# Create all database tables defined in models.py
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI(
    title="Hotel Management System API",
    description="API for managing hotel operations, including rooms, bookings, guests, and staff.",
    version="0.1.0",
)

# Root endpoint (already exists)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Hotel Management System API!"}

# --- User Authentication & Management Endpoints (updated) ---
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/users/", response_model=List[schemas.User], dependencies=[Depends(auth.RoleChecker(['admin']))])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(auth.RoleChecker(['admin']))])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(auth.RoleChecker(['admin']))])
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not crud.delete_user(db, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}

# --- Room Types Endpoints ---
@app.post("/room_types/", response_model=schemas.RoomType, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.RoleChecker(['admin']))])
def create_room_type(room_type: schemas.RoomTypeCreate, db: Session = Depends(get_db)):
    return crud.create_room_type(db=db, room_type=room_type)

@app.get("/room_types/", response_model=List[schemas.RoomType])
def read_room_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    room_types = crud.get_room_types(db, skip=skip, limit=limit)
    return room_types

@app.get("/room_types/{room_type_id}", response_model=schemas.RoomType)
def read_room_type(room_type_id: int, db: Session = Depends(get_db)):
    db_room_type = crud.get_room_type(db, room_type_id)
    if not db_room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    return db_room_type

@app.put("/room_types/{room_type_id}", response_model=schemas.RoomType, dependencies=[Depends(auth.RoleChecker(['admin']))])
def update_room_type(room_type_id: int, room_type: schemas.RoomTypeCreate, db: Session = Depends(get_db)):
    db_room_type = crud.update_room_type(db, room_type_id, room_type)
    if not db_room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    return db_room_type

@app.delete("/room_types/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_room_type(room_type_id: int, db: Session = Depends(get_db)):
    if not crud.delete_room_type(db, room_type_id):
        raise HTTPException(status_code=404, detail="Room type not found")
    return {"message": "Room type deleted successfully"}

# --- Room Endpoints ---
@app.post("/rooms/", response_model=schemas.Room, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.RoleChecker(['admin']))])
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_number(db, room.room_number)
    if db_room:
        raise HTTPException(status_code=400, detail="Room number already exists")
    db_room_type = crud.get_room_type(db, room.room_type_id)
    if not db_room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    return crud.create_room(db=db, room=room)

@app.get("/rooms/", response_model=List[schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, status: Optional[str] = None, room_type_id: Optional[int] = None, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit, status=status, room_type_id=room_type_id)
    return rooms

@app.get("/rooms/{room_id}", response_model=schemas.Room)
def read_room(room_id: int, db: Session = Depends(get_db)):
    db_room = crud.get_room(db, room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

@app.put("/rooms/{room_id}", response_model=schemas.Room, dependencies=[Depends(auth.RoleChecker(['admin']))])
def update_room(room_id: int, room: schemas.RoomUpdate, db: Session = Depends(get_db)):
    db_room = crud.update_room(db, room_id, room)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

@app.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_room(room_id: int, db: Session = Depends(get_db)):
    if not crud.delete_room(db, room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room deleted successfully"}

# --- Guest Endpoints ---
@app.post("/guests/", response_model=schemas.Guest, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def create_guest(guest: schemas.GuestCreate, db: Session = Depends(get_db)):
    db_guest = crud.get_guest_by_email(db, guest.email)
    if db_guest:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_guest(db=db, guest=guest)

@app.get("/guests/", response_model=List[schemas.Guest], dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def read_guests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    guests = crud.get_guests(db, skip=skip, limit=limit)
    return guests

@app.get("/guests/{guest_id}", response_model=schemas.Guest, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def read_guest(guest_id: int, db: Session = Depends(get_db)):
    db_guest = crud.get_guest(db, guest_id)
    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return db_guest

@app.put("/guests/{guest_id}", response_model=schemas.Guest, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def update_guest(guest_id: int, guest: schemas.GuestCreate, db: Session = Depends(get_db)):
    db_guest = crud.update_guest(db, guest_id, guest)
    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return db_guest

@app.delete("/guests/{guest_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    if not crud.delete_guest(db, guest_id):
        raise HTTPException(status_code=404, detail="Guest not found")
    return {"message": "Guest deleted successfully"}

# --- Booking Endpoints ---
@app.post("/bookings/", response_model=schemas.Booking, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.RoleChecker(['receiptionist', 'admin']))])
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    guest = crud.get_guest(db, booking.guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    room = crud.get_room(db, booking.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return crud.create_booking(db=db, booking=booking)

@app.get("/bookings/", response_model=List[schemas.Booking], dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def read_bookings(skip: int = 0, limit: int = 100, status: Optional[str] = None, guest_id: Optional[int] = None, room_id: Optional[int] = None, db: Session = Depends(get_db)):
    bookings = crud.get_bookings(db, skip=skip, limit=limit, status=status, guest_id=guest_id, room_id=room_id)
    return bookings

@app.get("/bookings/{booking_id}", response_model=schemas.Booking, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.get_booking(db, booking_id)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking

@app.put("/bookings/{booking_id}", response_model=schemas.Booking, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def update_booking(booking_id: int, booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    db_booking = crud.update_booking(db, booking_id, booking)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking

@app.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    if not crud.delete_booking(db, booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted successfully"}

# --- Services Endpoints ---
@app.post("/services/", response_model=schemas.Service, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.RoleChecker(['admin']))])
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    return crud.create_service(db=db, service=service)

@app.get("/services/", response_model=List[schemas.Service])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    services = crud.get_services(db, skip=skip, limit=limit)
    return services

@app.get("/services/{service_id}", response_model=schemas.Service)
def read_service(service_id: int, db: Session = Depends(get_db)):
    db_service = crud.get_service(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

@app.put("/services/{service_id}", response_model=schemas.Service, dependencies=[Depends(auth.RoleChecker(['admin']))])
def update_service(service_id: int, service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db_service = crud.update_service(db, service_id, service)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

@app.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_service(service_id: int, db: Session = Depends(get_db)):
    if not crud.delete_service(db, service_id):
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}

# --- Service Order Endpoints ---
@app.post("/service_orders/", response_model=schemas.ServiceOrder, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def create_service_order(service_order: schemas.ServiceOrderCreate, db: Session = Depends(get_db)):
    db_service = crud.get_service(db, service_order.service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    expected_amount = Decimal(str(db_service.price)) * Decimal(str(service_order.quantity))
    if abs(expected_amount - Decimal(str(service_order.total_amount))) > 0.01:
        raise HTTPException(status_code=400, detail=f"Total amount mismatch. Expected {expected_amount:.2f}")

    return crud.create_service_order(db=db, service_order=service_order)

@app.get("/service_orders/", response_model=List[schemas.ServiceOrder], dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def read_service_orders(skip: int = 0, limit: int = 100, booking_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    orders = crud.get_service_orders(db, skip=skip, limit=limit, booking_id=booking_id, status=status)
    return orders

@app.get("/service_orders/{order_id}", response_model=schemas.ServiceOrder, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def read_service_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_service_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Service order not found")
    return db_order

@app.put("/service_orders/{order_id}", response_model=schemas.ServiceOrder, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def update_service_order(order_id: int, service_order: schemas.ServiceOrderBase, db: Session = Depends(get_db)):
    db_order = crud.update_service_order(db, order_id, service_order)
    if not db_order:
        raise HTTPException(status_code=404, detail="Service order not found")
    return db_order

@app.delete("/service_orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_service_order(order_id: int, db: Session = Depends(get_db)):
    if not crud.delete_service_order(db, order_id):
        raise HTTPException(status_code=404, detail="Service order not found")
    return {"message": "Service order deleted successfully"}

# --- Housekeeping Task Endpoints ---
@app.post("/housekeeping_tasks/", response_model=schemas.HousekeepingTask, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.RoleChecker(['receptionist', 'admin']))])
def create_housekeeping_task(task: schemas.HousekeepingTaskCreate, db: Session = Depends(get_db)):
    return crud.create_housekeeping_task(db=db, task=task)

@app.get("/housekeeping_tasks/", response_model=List[schemas.HousekeepingTask], dependencies=[Depends(auth.RoleChecker(['housekeeping', 'admin']))])
def read_housekeeping_tasks(skip: int = 0, limit: int = 100, room_id: Optional[int] = None, status: Optional[str] = None, assigned_to_user_id: Optional[int] = None, db: Session = Depends(get_db)):
    tasks = crud.get_housekeeping_tasks(db, skip=skip, limit=limit, room_id=room_id, status=status, assigned_to_user_id=assigned_to_user_id)
    return tasks

@app.get("/housekeeping_tasks/{task_id}", response_model=schemas.HousekeepingTask, dependencies=[Depends(auth.RoleChecker(['housekeeping', 'admin']))])
def read_housekeeping_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_housekeeping_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Housekeeping task not found")
    return db_task

@app.put("/housekeeping_tasks/{task_id}", response_model=schemas.HousekeepingTask, dependencies=[Depends(auth.RoleChecker(['housekeeping', 'admin']))])
def update_housekeeping_task(task_id: int, task: schemas.HousekeepingTaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_housekeeping_task(db, task_id, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="Housekeeping task not found")
    return db_task

@app.delete("/housekeeping_tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.RoleChecker(['admin']))])
def delete_housekeeping_task(task_id: int, db: Session = Depends(get_db)):
    if not crud.delete_housekeeping_task(db, task_id):
        raise HTTPException(status_code=404, detail="Housekeeping task not found")
    return {"message": "Housekeeping task deleted successfully"}