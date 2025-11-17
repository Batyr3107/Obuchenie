from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.course import CourseFormat, PriceType, DifficultyLevel, CourseStatus
from app.core.sanitizer import sanitize_text, sanitize_html, sanitize_url


# Course Create
class CourseCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    short_description: str = Field(..., min_length=10, max_length=300)
    full_description: Optional[str] = None
    official_url: str
    logo_url: Optional[str] = None

    category_id: int
    subcategory_id: Optional[int] = None

    format: CourseFormat
    price_type: PriceType
    price_amount: Optional[float] = None
    currency: str = "USD"

    duration_hours: Optional[int] = None
    duration_weeks: Optional[int] = None

    language: str = "ru"
    has_certificate: bool = False
    difficulty_level: Optional[DifficultyLevel] = None

    requirements: Optional[str] = None
    what_you_learn: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None

    tags: Optional[List[str]] = []

    @field_validator('title', 'short_description')
    @classmethod
    def sanitize_titles(cls, v):
        """Санитизация заголовков и описаний"""
        return sanitize_text(v) if v else v

    @field_validator('full_description', 'requirements', 'what_you_learn')
    @classmethod
    def sanitize_descriptions(cls, v):
        """Санитизация полных описаний (разрешаем базовые HTML теги)"""
        return sanitize_html(v, strip=False) if v else v

    @field_validator('official_url', 'logo_url')
    @classmethod
    def sanitize_urls(cls, v):
        """Санитизация URL"""
        if v:
            sanitized = sanitize_url(v)
            if not sanitized:
                raise ValueError("Invalid URL format")
            return sanitized
        return v

    @field_validator('tags')
    @classmethod
    def sanitize_tags(cls, v):
        """Санитизация тегов"""
        if v is None:
            return []
        return [sanitize_text(tag, max_length=50) for tag in v if tag]


# Course Update
class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    short_description: Optional[str] = Field(None, min_length=10, max_length=300)
    full_description: Optional[str] = None
    official_url: Optional[str] = None
    logo_url: Optional[str] = None

    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None

    format: Optional[CourseFormat] = None
    price_type: Optional[PriceType] = None
    price_amount: Optional[float] = None

    duration_hours: Optional[int] = None
    duration_weeks: Optional[int] = None

    language: Optional[str] = None
    has_certificate: Optional[bool] = None
    difficulty_level: Optional[DifficultyLevel] = None

    requirements: Optional[str] = None
    what_you_learn: Optional[str] = None

    @field_validator('title', 'short_description')
    @classmethod
    def sanitize_titles(cls, v):
        """Санитизация заголовков и описаний"""
        return sanitize_text(v) if v else v

    @field_validator('full_description', 'requirements', 'what_you_learn')
    @classmethod
    def sanitize_descriptions(cls, v):
        """Санитизация полных описаний (разрешаем базовые HTML теги)"""
        return sanitize_html(v, strip=False) if v else v

    @field_validator('official_url', 'logo_url')
    @classmethod
    def sanitize_urls(cls, v):
        """Санитизация URL"""
        if v:
            sanitized = sanitize_url(v)
            if not sanitized:
                raise ValueError("Invalid URL format")
            return sanitized
        return v


# Course Response
class CourseResponse(BaseModel):
    id: int
    title: str
    slug: str
    short_description: str
    official_url: str
    logo_url: Optional[str]

    category_id: int
    subcategory_id: Optional[int]

    format: CourseFormat
    price_type: PriceType
    price_amount: Optional[float]
    currency: str

    duration_hours: Optional[int]
    duration_weeks: Optional[int]

    language: str
    has_certificate: bool
    difficulty_level: Optional[DifficultyLevel]

    status: CourseStatus
    is_verified: bool

    avg_rating: float
    total_reviews: int

    avg_content_quality: float
    avg_instructors: float
    avg_support: float
    avg_price_quality: float
    avg_practical: float

    views_count: int
    favorites_count: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Course List (краткая версия для списков)
class CourseListItem(BaseModel):
    id: int
    title: str
    slug: str
    short_description: str
    logo_url: Optional[str]
    avg_rating: float
    total_reviews: int
    price_type: PriceType
    price_amount: Optional[float]
    currency: str

    class Config:
        from_attributes = True
