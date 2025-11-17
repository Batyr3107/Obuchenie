from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re
from app.models.user import UserRole, UserLevel


# User Registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """
        Validate password complexity:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')

        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty123', 'admin123']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')

        return v


# User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# User Update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


# User Response
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: UserRole
    level: UserLevel
    is_active: bool
    is_verified: bool
    reputation_score: int
    helpful_votes: int
    created_at: datetime

    class Config:
        from_attributes = True
