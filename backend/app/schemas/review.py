from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.review import CompletionStatus


# Review Create
class ReviewCreate(BaseModel):
    course_id: int

    # Оценки (1-5)
    content_quality: float = Field(..., ge=1, le=5)
    instructors: float = Field(..., ge=1, le=5)
    support: float = Field(..., ge=1, le=5)
    price_quality: float = Field(..., ge=1, le=5)
    practical: float = Field(..., ge=1, le=5)

    # Текст отзыва
    review_text: str = Field(..., min_length=100)
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []

    # Дополнительно
    recommend: bool = True
    completion_status: CompletionStatus
    completion_date: Optional[str] = None  # YYYY-MM


# Review Update
class ReviewUpdate(BaseModel):
    content_quality: Optional[float] = Field(None, ge=1, le=5)
    instructors: Optional[float] = Field(None, ge=1, le=5)
    support: Optional[float] = Field(None, ge=1, le=5)
    price_quality: Optional[float] = Field(None, ge=1, le=5)
    practical: Optional[float] = Field(None, ge=1, le=5)

    review_text: Optional[str] = Field(None, min_length=100)
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None

    recommend: Optional[bool] = None
    completion_status: Optional[CompletionStatus] = None
    completion_date: Optional[str] = None


# Review Response
class ReviewResponse(BaseModel):
    id: int
    user_id: int
    course_id: int

    content_quality: float
    instructors: float
    support: float
    price_quality: float
    practical: float
    overall_rating: float

    review_text: str
    pros: Optional[List[str]]
    cons: Optional[List[str]]

    recommend: bool
    completion_status: CompletionStatus
    completion_date: Optional[str]

    helpful_count: int
    not_helpful_count: int

    is_approved: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
