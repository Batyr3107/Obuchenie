"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base, get_db


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """
    Test user data fixture

    SECURITY: Test credentials are isolated to test environment
    """
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }


@pytest.fixture
def admin_user_data():
    """Admin user data for testing admin functionality"""
    return {
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "full_name": "Admin User"
    }


@pytest.fixture
def weak_password_data():
    """Weak password data for testing password validation"""
    return [
        "123",
        "password",
        "12345678",
        "qwerty"
    ]


@pytest.fixture
def strong_password_data():
    """Strong password data for testing password validation"""
    return [
        "SecurePass123!",
        "MyStr0ng!Pass",
        "Test@Pass2024"
    ]


@pytest.fixture
def test_course_data():
    """Test course data"""
    return {
        "title": "Test Course",
        "short_description": "This is a test course for automated testing purposes",
        "official_url": "https://example.com/course",
        "category_id": 1,
        "format": "online",
        "price_type": "free",
        "language": "ru"
    }


@pytest.fixture
def test_review_data():
    """Test review data"""
    return {
        "rating": 5.0,
        "content_quality": 5.0,
        "instructors": 5.0,
        "support": 4.0,
        "price_quality": 5.0,
        "practical": 4.5,
        "comment": "Great course! Highly recommended."
    }


@pytest.fixture
def test_category_data():
    """Test category data"""
    return {
        "name": "Test Category",
        "slug": "test-category",
        "description": "This is a test category",
        "icon": "test-icon"
    }
