from pydantic import BaseModel, Field, EmailStr
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
