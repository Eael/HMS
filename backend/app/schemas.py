from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List
import datetime



# --- User Schema ---

# Base schema for user attributes
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50) # ... means this field is required
    email: EmailStr # Email validation
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=500)

    # Role will be validated against the Enum defined in the model
    role: str = Field(default='guest', pattern='^(admin|receiptionist|housekeeping|guest)$')


# Schema for creating a new user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)  # Password must be at least 8 characters


# Schema for updating an existing user (all fields are optional)
class UserUpdate(UserBase):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None  # Email can be updated, but must be valid
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=500)
    role: Optional[str] = Field(None, pattern='^(admin|receiptionist|housekeeping|guest)$')
    password: Optional[str] = Field(None, min_length=8, max_length=128)  # Password is optional for updates


# Schema for user response (used when returning user data)
class User(UserBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True  # This allows Pydantic to read data from SQLAlchemy models


# --- Token Schemas for Authentication ---

# Schema for the JWT access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Schema for token response, including user information
class TokenData(BaseModel):
    username: Optional[str] = None

# --- Room Type Schemas ---
class RoomTypeBase(BaseModel):
    type_name: str = Field(..., max_length=50)  # e.g., Standard, Suite, Deluxe
    capacity: int = Field(..., gt=0)  # Max number of guests
    base_price: int = Field(..., gt=0)  # Base price per night
    description: Optional[str] = Field(None, max_length=500)

class RoomTypeCreate(RoomTypeBase):
    pass

class RoomTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)
    base_price: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)

class RoomType(RoomTypeBase):
    id: int

    class Config:
        from_attributes = True


# --- Room Schemas ---
class RoomBase(BaseModel):
    room_number: str = Field(..., max_length=10)
    room_type_id: int
    status: str = Field(default='available', pattern='^(available|occupied|cleaning|maintenance)$')
    floor: int = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_number: Optional[str] = Field(None, max_length=10)
    room_type_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern='^(available|occupied|cleaning|maintenance)$')
    floor: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)

class Room(RoomBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    room_type: Optional[RoomType] = None  # Nested RoomType schema

    class Config:
        from_attributes = True

# --- Guest Schemas ---

class GuestBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=500)
    id_document_type: Optional[str] = Field(None, max_length=50)  # e.g., 'Passport', 'ID Card'
    id_document_number: Optional[str] = Field(None, max_length=100)

class GuestCreate(GuestBase):
    pass

class GuestUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=500)
    id_document_type: Optional[str] = Field(None, max_length=50)
    id_document_number: Optional[str] = Field(None, max_length=100)

class Guest(GuestBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

# --- Booking Schemas ---
class BookingBase(BaseModel):
    room_id: int
    guest_id: int
    check_in_date: datetime.date
    check_out_date: datetime.date
    num_guests: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    booking_status: str = Field(default='pending', pattern='^(pending|confirmed|checked_in|checked_out|cancelled)$')
    payment_status: str = Field(default='pending', pattern='^(pending|paid|refunded)$')


    @model_validator(mode='after')
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError('Check-out date must be after check-in date')
        return self


class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    room_id: Optional[int] = None
    guest_id: Optional[int] = None
    check_in_date: Optional[datetime.date] = None
    check_out_date: Optional[datetime.date] = None
    num_guests: Optional[int] = Field(None, gt=0)
    total_price: Optional[float] = Field(None, gt=0)
    booking_status: Optional[str] = Field(None, pattern='^(pending|confirmed|checked_in|checked_out|cancelled)$')
    payment_status: Optional[str] = Field(None, pattern='^(pending|paid|refunded)$')

    @model_validator(mode='after')
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError('Check-out date must be after check-in date')
        return self

    
class Booking(BookingBase):
    id: int
    booked_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    guest: Optional[Guest] = None  # Nested Guest schema
    room: Optional[Room] = None    # Nested Room schema

    class Config:
        from_attributes = True

# --- Payment Schemas ---
class PaymentBase(BaseModel):
    booking_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., max_length=50)  # e.g., 'Credit Card', 'Cash', 'Online Transfer'
    transaction_id: Optional[str] = Field(None, max_length=100)  # Optional external transaction ID

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    booking_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    transaction_id: Optional[str] = Field(None, max_length=100)

class Payment(PaymentBase):
    id: int
    payment_date: datetime.datetime
    booking: Optional[Booking] = None  # Nested Booking schema

    class Config:
        from_attributes = True

# --- Service Schemas ---
class ServiceBase(BaseModel):
    service_name: str = Field(..., max_length=100)  # e.g., 'Room Service', 'Laundry', 'Spa'
    price: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    service_name: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)

class Service(ServiceBase):
    id: int
    class Config:
        from_attributes = True

# --- ServiceOrder Schemas ---
class ServiceOrderBase(BaseModel):
    booking_id: int
    service_id: int
    quantity: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    order_status: str = Field(default='pending', pattern='^(pending|completed|cancelled)$')

class ServiceOrderCreate(ServiceOrderBase):
    pass

class ServiceOrderUpdate(BaseModel):
    booking_id: Optional[int] = None
    service_id: Optional[int] = None
    quantity: Optional[int] = Field(None, gt=0)
    total_price: Optional[float] = Field(None, gt=0)
    order_status: Optional[str] = Field(None, pattern='^(pending|completed|cancelled)$')

class ServiceOrder(ServiceOrderBase):
    id: int
    order_date: datetime.datetime
    booking: Optional[Booking] = None  # Nested Booking schema
    service: Optional[Service] = None   # Nested Service schema

    class Config:
        from_attributes = True

# --- Housekeeping Task Schemas ---

class HousekeepingTaskBase(BaseModel):
    room_id: int
    assigned_to_id: Optional[int] = None  # User ID of the staff assigned
    status: str = Field("pending", pattern="^(pending|in_progress|completed|cancelled)$")
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    due_date: datetime.date
    notes: Optional[str] = None

class HousekeepingTaskCreate(HousekeepingTaskBase):
    pass

class HousekeepingTaskUpdate(BaseModel):
    room_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    due_date: Optional[datetime.date] = None
    notes: Optional[str] = None

class HousekeepingTask(HousekeepingTaskBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    room: Optional[Room] = None  # Nested Room schema
    assigned_to: Optional[User] = None  # Nested User schema

    class Config:
        from_attributes = True