"""
Basic API tests
"""
import pytest


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "CourseRate" in response.json()["message"]


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client, test_user_data):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert "password" not in data  # Password should not be in response


def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email"""
    # First registration
    client.post("/api/v1/auth/register", json=test_user_data)

    # Second registration with same email
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register user first
    client.post("/api/v1/auth/register", json=test_user_data)

    # Login
    response = client.post("/api/v1/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user_data):
    """Test login with invalid credentials"""
    response = client.post("/api/v1/auth/login", data={
        "username": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_courses_without_auth(client):
    """Test getting courses without authentication"""
    response = client.get("/api/v1/courses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_course_without_auth(client, test_course_data):
    """Test creating course without authentication"""
    response = client.post("/api/v1/courses", json=test_course_data)
    assert response.status_code == 401  # Should require authentication


def test_get_categories(client):
    """Test getting categories"""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_endpoints_without_auth(client):
    """Test admin endpoints require authentication"""
    endpoints = [
        "/api/v1/admin/stats",
        "/api/v1/admin/courses/pending",
        "/api/v1/admin/users",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401  # Unauthorized


def test_favorites_without_auth(client):
    """Test favorites require authentication"""
    response = client.get("/api/v1/favorites")
    assert response.status_code == 401


def test_search_autocomplete(client):
    """Test search autocomplete"""
    response = client.get("/api/v1/search/autocomplete?q=python")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_autocomplete_short_query(client):
    """Test search autocomplete with too short query"""
    response = client.get("/api/v1/search/autocomplete?q=p")
    assert response.status_code == 422  # Validation error
