from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, UserLevel


# User Registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


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
