from sqlalchemy import Column, Date, Integer, String, DateTime, ForeignKey, Enum, Text, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base # Import the Base class from database.py


# Define the User model
class User(Base):
    """User model representing a user in the system."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    # Define roles using an Enum
    role = Column(Enum('admin', 'receptionist', 'housekeeping', 'guest', name='user_roles'), default='guest')
    phone_number = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define a relationship to HousekeepingTask, indicating a user can be assigned multiple tasks
    assigned_housekeeping_tasks = relationship("HousekeepingTask", back_populates="assigned_to_user")

    # __repr__ method for better debugging
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
# Define Room types
class RoomType(Base):
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, nullable=False) # e.g Standard, Suite, Deluxe
    capacity = Column(Integer, nullable=False) # max number of guests
    base_price = Column(Integer, nullable=False) # base price per night
    description = Column(Text, nullable=True)
    
    rooms = relationship("Room", back_populates="room_type")

    def __repr__(self):
        return f"<RoomType(id={self.id}, type_name={self.type_name}, capacity={self.capacity}, price={self.base_price})>"


# Define the Room model
class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, index=True, nullable=False)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False)
    status = Column(Enum('available', 'occupied', 'cleaning', 'maintenance', name='room_status'), default='available')
    floor = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationships
    room_type = relationship("RoomType", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")
    housekeeping_tasks = relationship("HousekeepingTask", back_populates="room")

    def __repr__(self):
        return f"<Room(id={self.id}, number='{self.room_number}', type_id={self.room_type_id}, status='{self.status}', floor={self.floor})>"
    
# Guest Model
class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    id_document_type = Column(String, nullable=True) # e.g., 'Passport', 'ID Card'
    id_document_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define a relationship to Booking
    bookings = relationship("Booking", back_populates="guest")

    def __repr__(self):
        return f"<Guest(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"

# Booking Model
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False) # Foreign key to Guest
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False) # Foreign key to Room
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    num_guests = Column(Integer, nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    booking_status = Column(Enum('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', name='booking_status'), default='pending', nullable=False)
    payment_status = Column(Enum('pending', 'paid', 'refunded', name='payment_status'), default='pending', nullable=False)
    booked_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationships
    guest = relationship("Guest", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
    service_orders = relationship("ServiceOrder", back_populates="booking")

    def __repr__(self):
        return f"<Booking(id={self.id}, guest_id={self.guest_id}, room_id={self.room_id}, status='{self.booking_status}')>"

# Payment Model
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False) # Foreign key to Booking
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String, nullable=False) # e.g., 'Credit Card', 'Cash', 'Online Transfer'
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    transaction_id = Column(String, unique=True, index=True, nullable=True) # Optional external transaction ID

    # Define relationship
    booking = relationship("Booking", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, booking_id={self.booking_id}, amount={self.amount}, method='{self.payment_method}')>"

# Service Model
class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True, index=True, nullable=False) # e.g., 'Room Service', 'Laundry', 'Spa'
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text, nullable=True)

    # Define relationship
    service_orders = relationship("ServiceOrder", back_populates="service")

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.service_name}', price={self.price})>"

# ServiceOrder Model
class ServiceOrder(Base):
    __tablename__ = "service_orders"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False) # Foreign key to Booking
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False) # Foreign key to Service
    quantity = Column(Integer, default=1, nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum('pending', 'completed', 'cancelled', name='service_order_status'), default='pending', nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False) # Calculated based on service price * quantity

    # Define relationships
    booking = relationship("Booking", back_populates="service_orders")
    service = relationship("Service", back_populates="service_orders")

    def __repr__(self):
        return f"<ServiceOrder(id={self.id}, booking_id={self.booking_id}, service_id={self.service_id}, status='{self.status}')>"

# HousekeepingTask Model
class HousekeepingTask(Base):
    __tablename__ = "housekeeping_tasks"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False) # Foreign key to Room
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Foreign key to User (housekeeping staff)
    status = Column(Enum('pending', 'in_progress', 'completed', 'cancelled', name='task_status'), default='pending', nullable=False)
    priority = Column(Enum('low', 'medium', 'high', name='task_priority'), default='medium', nullable=False)
    due_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationships
    room = relationship("Room", back_populates="housekeeping_tasks")
    assigned_to_user = relationship("User", back_populates="assigned_housekeeping_tasks")

    def __repr__(self):
        return f"<HousekeepingTask(id={self.id}, room_id={self.room_id}, status='{self.status}', due='{self.due_date}')>"