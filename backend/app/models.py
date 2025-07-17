from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
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
    role = Column(Enum('admin', 'receiptionist', 'housekeeping', 'guest', name='user_roles'), default='guest')
    phone_number = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # __repr__ method for better debugging
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
