from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

# Many-to-Many таблица для курсов и тегов
course_tags = Table(
    'course_tags',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)


class CourseFormat(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"


class PriceType(str, enum.Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)

    # Основная информация
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    short_description = Column(String(300), nullable=False)
    full_description = Column(Text, nullable=True)

    # Ссылки и медиа
    official_url = Column(String(500), nullable=False)
    logo_url = Column(String(500), nullable=True)

    # Категории
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=True)

    # Характеристики курса
    format = Column(SQLEnum(CourseFormat), nullable=False)
    price_type = Column(SQLEnum(PriceType), nullable=False)
    price_amount = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")

    duration_hours = Column(Integer, nullable=True)
    duration_weeks = Column(Integer, nullable=True)

    language = Column(String(50), nullable=False, default="ru")
    has_certificate = Column(Boolean, default=False)
    difficulty_level = Column(SQLEnum(DifficultyLevel), nullable=True)

    # Дополнительная информация
    requirements = Column(Text, nullable=True)
    what_you_learn = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Статус и модерация
    status = Column(SQLEnum(CourseStatus), default=CourseStatus.PENDING)
    is_verified = Column(Boolean, default=False)

    # Рейтинг (автоматически рассчитывается)
    avg_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    # Детальные рейтинги
    avg_content_quality = Column(Float, default=0.0)
    avg_instructors = Column(Float, default=0.0)
    avg_support = Column(Float, default=0.0)
    avg_price_quality = Column(Float, default=0.0)
    avg_practical = Column(Float, default=0.0)

    # Статистика
    views_count = Column(Integer, default=0)
    favorites_count = Column(Integer, default=0)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="courses")
    subcategory = relationship("Subcategory", back_populates="courses")
    reviews = relationship("Review", back_populates="course", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="course", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=course_tags, back_populates="courses")
    premium_placement = relationship("PremiumPlacement", back_populates="course", uselist=False)
