from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text
from typing import Optional
from . import models, schemas
from .auth import hash_password
import datetime



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

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user by ID."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# --- Room CRUD operations ---
def get_room(db: Session, room_id: int) -> Optional[models.Room]:
    """Get a room by ID."""
    return db.query(models.Room).filter(models.Room.id == room_id).first()

def get_room_by_number(db: Session, room_number: str) -> Optional[models.Room]:
    """Get a room by room number."""
    return db.query(models.Room).filter(models.Room.room_number == room_number).first()

def get_rooms(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, room_type_id: Optional[int] = None) -> list[models.Room]:
    """Get a list of rooms with pagination."""
    query = db.query(models.Room)
    if status:
        query = query.filter(models.Room.status == status)
    if room_type_id:
        query = query.filter(models.Room.room_type_id == room_type_id)

    return query.offset(skip).limit(limit).all()

def create_room(db: Session, room: schemas.RoomCreate) -> models.Room:
    """Create a new room."""
    db_room = models.Room(
        room_number=room.room_number,
        room_type_id=room.room_type_id,
        status=room.status if room.status else 'available',
        floor=room.floor,
        description=room.description if room.description else None
    )
    db.add(db_room) # Add the new room to the session
    db.commit() # Commit the session to save the room
    db.refresh(db_room) # Refresh the instance to get the updated data
    return db_room

def update_room(db: Session, room_id: int, room_update: schemas.RoomUpdate) -> Optional[models.Room]:
    """Update an existing room."""
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        return None

    # Update fields if provided
    for key, value in room_update.model_dump(exclude_unset=True).items():
        setattr(db_room, key, value)

    db.commit() # Commit the session to save changes
    db.refresh(db_room) # Refresh the instance to get the updated data
    return db_room

def delete_room(db: Session, room_id: int) -> bool:
    """Delete a room by ID."""
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room:
        db.delete(db_room)
        db.commit()
        return True
    return False

# --- Room Type CRUD operations ---
def get_room_type(db: Session, room_type_id: int) -> Optional[models.RoomType]:
    """Get a room type by ID."""
    return db.query(models.RoomType).filter(models.RoomType.id == room_type_id).first()

def get_room_type_by_name(db: Session, type_name: str) -> Optional[models.RoomType]:
    """Get a room type by name."""
    return db.query(models.RoomType).filter(models.RoomType.type_name == type_name).first()

def get_room_types(db: Session, skip: int = 0, limit: int = 100) -> list[models.RoomType]:
    """Get a list of room types with pagination."""
    return db.query(models.RoomType).offset(skip).limit(limit).all()

def create_room_type(db: Session, room_type: schemas.RoomTypeCreate) -> models.RoomType:
    """Create a new room type."""
    db_room_type = models.RoomType(**room_type.model_dump())
    db.add(db_room_type) # Add the new room type to the session
    db.commit() # Commit the session to save the room type
    db.refresh(db_room_type) # Refresh the instance to get the updated data
    return db_room_type

def update_room_type(db: Session, room_type_id: int, room_type_update: schemas.RoomTypeUpdate) -> Optional[models.RoomType]:
    """Update an existing room type."""
    db_room_type = db.query(models.RoomType).filter(models.RoomType.id == room_type_id).first()
    if not db_room_type:
        return None

    # Update fields if provided
    for key, value in room_type_update.model_dump(exclude_unset=True).items():
        setattr(db_room_type, key, value)

    db.commit() # Commit the session to save changes
    db.refresh(db_room_type) # Refresh the instance to get the updated data
    return db_room_type

def delete_room_type(db: Session, room_type_id: int) -> bool:
    """Delete a room type by ID."""
    db_room_type = db.query(models.RoomType).filter(models.RoomType.id == room_type_id).first()
    if db_room_type:
        db.delete(db_room_type)
        db.commit()
        return True
    return False


# --- Guest CRUD operations ---
def get_guest(db: Session, guest_id: int) -> Optional[models.Guest]:
    """Get a guest by ID."""
    return db.query(models.Guest).filter(models.Guest.id == guest_id).first()

def get_guest_by_email(db: Session, email: str) -> Optional[models.Guest]:
    """Get a guest by email."""
    return db.query(models.Guest).filter(models.Guest.email == email).first()

def get_guests(db: Session, skip: int = 0, limit: int = 100) -> list[models.Guest]:
    """Get a list of guests with pagination."""
    return db.query(models.Guest).offset(skip).limit(limit).all()

def create_guest(db: Session, guest: schemas.GuestCreate) -> models.Guest:
    """Create a new guest."""
    db_guest = models.Guest(**guest.model_dump())
    db.add(db_guest) # Add the new guest to the session
    db.commit() # Commit the session to save the guest
    db.refresh(db_guest) # Refresh the instance to get the updated data
    return db_guest

def update_guest(db: Session, guest_id: int, guest_update: schemas.GuestUpdate) -> Optional[models.Guest]:
    """Update an existing guest."""
    db_guest = db.query(models.Guest).filter(models.Guest.id == guest_id).first()
    if not db_guest:
        return None

    # Update fields if provided
    for key, value in guest_update.model_dump(exclude_unset=True).items():
        setattr(db_guest, key, value)

    db.commit() # Commit the session to save changes
    db.refresh(db_guest) # Refresh the instance to get the updated data
    return db_guest

def delete_guest(db: Session, guest_id: int) -> bool:
    """Delete a guest by ID."""
    db_guest = db.query(models.Guest).filter(models.Guest.id == guest_id).first()
    if db_guest:
        db.delete(db_guest)
        db.commit()
        return True
    return False

# --- Booking CRUD operations ---
def get_booking(db: Session, booking_id: int) -> Optional[models.Booking]:
    """Get a booking by ID."""
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()

def get_bookings(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, guest_id: Optional[int] = None, room_id: Optional[int] = None) -> list[models.Booking]:
    """Get a list of bookings with pagination."""
    query = db.query(models.Booking)
    if status:
        query = query.filter(models.Booking.booking_status == status)
    if guest_id:
        query = query.filter(models.Booking.guest_id == guest_id)
    if room_id:
        query = query.filter(models.Booking.room_id == room_id)

    return query.offset(skip).limit(limit).all()

def create_booking(db: Session, booking: schemas.BookingCreate) -> models.Booking:
    """Create a new booking."""
    db_booking = models.Booking(**booking.model_dump())
    db.add(db_booking) # Add the new booking to the session
    db.commit() # Commit the session to save the booking
    db.refresh(db_booking) # Refresh the instance to get the updated data
    return db_booking

def update_booking(db: Session, booking_id: int, booking_update: schemas.BookingUpdate) -> Optional[models.Booking]:
    """Update an existing booking."""
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not db_booking:
        return None

    # Update fields if provided
    for key, value in booking_update.model_dump(exclude_unset=True).items():
        setattr(db_booking, key, value)

    db.commit() # Commit the session to save changes
    db.refresh(db_booking) # Refresh the instance to get the updated data
    return db_booking

def delete_booking(db: Session, booking_id: int) -> bool:
    """Delete a booking by ID."""
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
        return True
    return False

# --- Housekeeping Task CRUD operations ---
def get_housekeeping_task(db: Session, task_id: int) -> Optional[models.HousekeepingTask]:
    """Get a housekeeping task by ID."""
    return db.query(models.HousekeepingTask).filter(models.HousekeepingTask.id == task_id).first()

def get_housekeeping_tasks(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, room_id: Optional[int] = None) -> list[models.HousekeepingTask]:
    """Get a list of housekeeping tasks with pagination."""
    query = db.query(models.HousekeepingTask)
    if status:
        query = query.filter(models.HousekeepingTask.status == status)
    if room_id:
        query = query.filter(models.HousekeepingTask.room_id == room_id)

    return query.offset(skip).limit(limit).all()

def create_housekeeping_task(db: Session, task: schemas.HousekeepingTaskCreate) -> models.HousekeepingTask:
    """Create a new housekeeping task."""
    db_task = models.HousekeepingTask(**task.model_dump())
    db.add(db_task) # Add the new task to the session
    db.commit() # Commit the session to save the task
    db.refresh(db_task) # Refresh the instance to get the updated data
    return db_task

def update_housekeeping_task(db: Session, task_id: int, task_update: schemas.HousekeepingTaskUpdate) -> Optional[models.HousekeepingTask]:
    """Update an existing housekeeping task."""
    db_task = db.query(models.HousekeepingTask).filter(models.HousekeepingTask.id == task_id).first()
    if not db_task:
        return None

    # Update fields if provided
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    db.commit() # Commit the session to save changes
    db.refresh(db_task) # Refresh the instance to get the updated data
    return db_task

def delete_housekeeping_task(db: Session, task_id: int) -> bool:
    """Delete a housekeeping task by ID."""
    db_task = db.query(models.HousekeepingTask).filter(models.HousekeepingTask.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

# --- Service CRUD operations ---
def get_service(db: Session, service_id: int) -> Optional[models.Service]:
    """Get a service by ID."""
    return db.query(models.Service).filter(models.Service.id == service_id).first()

def get_services(db: Session, skip: int = 0, limit: int = 100) -> list[models.Service]:
    """Get a list of services with pagination."""
    return db.query(models.Service).offset(skip).limit(limit).all()

def create_service(db: Session, service: schemas.ServiceCreate) -> models.Service:
    """Create a new service."""
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def update_service(db: Session, service_id: int, service_update: schemas.ServiceUpdate) -> Optional[models.Service]:
    """Update an existing service."""
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        return None

    for key, value in service_update.model_dump(exclude_unset=True).items():
        setattr(db_service, key, value)

    db.commit()
    db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int) -> bool:
    """Delete a service by ID."""
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if db_service:
        db.delete(db_service)
        db.commit()
        return True
    return False

# --- Service Order CRUD operations ---
def get_service_order(db: Session, order_id: int) -> Optional[models.ServiceOrder]:
    """Get a service order by ID."""
    return db.query(models.ServiceOrder).filter(models.ServiceOrder.id == order_id).first()

def get_service_orders(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, booking_id: Optional[int] = None) -> list[models.ServiceOrder]:
    """Get a list of service orders with pagination."""
    query = db.query(models.ServiceOrder)
    if status:
        query = query.filter(models.ServiceOrder.status == status)
    if booking_id:
        query = query.filter(models.ServiceOrder.booking_id == booking_id)

    return query.offset(skip).limit(limit).all()


def create_service_order(db: Session, order: schemas.ServiceOrderCreate) -> models.ServiceOrder:
    """Create a new service order."""
    db_order = models.ServiceOrder(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_service_order(db: Session, order_id: int, order_update: schemas.ServiceOrderUpdate) -> Optional[models.ServiceOrder]:
    """Update an existing service order."""
    db_order = db.query(models.ServiceOrder).filter(models.ServiceOrder.id == order_id).first()
    if not db_order:
        return None

    for key, value in order_update.model_dump(exclude_unset=True).items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order

def delete_service_order(db: Session, order_id: int) -> bool:
    """Delete a service order by ID."""
    db_order = db.query(models.ServiceOrder).filter(models.ServiceOrder.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False

# --- Payment CRUD operations ---
def get_payment(db: Session, payment_id: int) -> Optional[models.Payment]:
    """Get a payment by ID."""
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()

def get_payments(db: Session, skip: int = 0, limit: int = 100, booking_id: Optional[int] = None) -> list[models.Payment]:
    """Get a list of payments with pagination."""
    query = db.query(models.Payment)
    if booking_id:
        query = query.filter(models.Payment.booking_id == booking_id)

    return query.offset(skip).limit(limit).all()

def create_payment(db: Session, payment: schemas.PaymentCreate) -> models.Payment:
    """Create a new payment."""
    db_payment = models.Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment(db: Session, payment_id: int, payment_update: schemas.PaymentUpdate) -> Optional[models.Payment]:
    """Update an existing payment."""
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not db_payment:
        return None

    for key, value in payment_update.model_dump(exclude_unset=True).items():
        setattr(db_payment, key, value)

    db.commit()
    db.refresh(db_payment)
    return db_payment


def delete_payment(db: Session, payment_id: int) -> bool:
    """Delete a payment by ID."""
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if db_payment:
        db.delete(db_payment)
        db.commit()
        return True
    return False