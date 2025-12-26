from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
import re
from datetime import datetime
from app.models.review import CompletionStatus
from app.core.sanitizer import sanitize_text, sanitize_html


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

    @field_validator('review_text')
    @classmethod
    def sanitize_review_text(cls, v):
        """Санитизация текста отзыва"""
        return sanitize_html(v, strip=True)

    @field_validator('pros', 'cons')
    @classmethod
    def sanitize_list_items(cls, v):
        """Санитизация элементов списков"""
        if v is None:
            return []
        return [sanitize_text(item, max_length=200) for item in v if item]

    @field_validator('completion_date')
    @classmethod
    def validate_completion_date(cls, v):
        """Validate completion_date format YYYY-MM"""
        if v is None:
            return v
        if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', v):
            raise ValueError('Date must be in YYYY-MM format (e.g., 2024-01)')
        year = int(v.split('-')[0])
        if year < 1990 or year > 2100:
            raise ValueError('Invalid year')
        return v


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

    @field_validator('review_text')
    @classmethod
    def sanitize_review_text(cls, v):
        """Санитизация текста отзыва"""
        if v is not None:
            return sanitize_html(v, strip=True)
        return v

    @field_validator('pros', 'cons')
    @classmethod
    def sanitize_list_items(cls, v):
        """Санитизация элементов списков"""
        if v is None:
            return None
        return [sanitize_text(item, max_length=200) for item in v if item]

    @field_validator('completion_date')
    @classmethod
    def validate_completion_date(cls, v):
        """Validate completion_date format YYYY-MM"""
        if v is None:
            return v
        if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', v):
            raise ValueError('Date must be in YYYY-MM format (e.g., 2024-01)')
        year = int(v.split('-')[0])
        if year < 1990 or year > 2100:
            raise ValueError('Invalid year')
        return v


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

    model_config = ConfigDict(from_attributes=True)
