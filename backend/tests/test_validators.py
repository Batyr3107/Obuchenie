"""
Tests for validators
"""
import pytest
from fastapi import HTTPException
from app.core.validators import (
    sanitize_text,
    validate_email,
    validate_url,
    validate_rating,
    detect_sql_injection,
    validate_search_query
)


def test_sanitize_text():
    """Test text sanitization"""
    # Remove HTML tags
    assert sanitize_text("<script>alert('xss')</script>Hello") == "Hello"

    # Remove extra spaces
    assert sanitize_text("Hello    World") == "Hello World"

    # Max length
    assert len(sanitize_text("a" * 1000, max_length=100)) == 100


def test_validate_email_valid():
    """Test valid email"""
    assert validate_email("test@example.com") == "test@example.com"
    assert validate_email("  TEST@EXAMPLE.COM  ") == "test@example.com"


def test_validate_email_invalid():
    """Test invalid emails"""
    invalid_emails = [
        "notanemail",
        "@example.com",
        "test@",
        "test<script>@example.com"
    ]

    for email in invalid_emails:
        with pytest.raises(HTTPException):
            validate_email(email)


def test_validate_url_valid():
    """Test valid URLs"""
    urls = [
        "https://example.com",
        "http://example.com/path",
        "https://sub.example.com"
    ]

    for url in urls:
        assert validate_url(url) == url


def test_validate_url_invalid():
    """Test invalid URLs"""
    invalid_urls = [
        "not a url",
        "ftp://example.com",  # Wrong scheme
        "example.com",  # No scheme
    ]

    for url in invalid_urls:
        with pytest.raises(HTTPException):
            validate_url(url)


def test_validate_rating_valid():
    """Test valid ratings"""
    assert validate_rating(5.0) == 5.0
    assert validate_rating(3.5) == 3.5
    assert validate_rating(1) == 1.0


def test_validate_rating_invalid():
    """Test invalid ratings"""
    with pytest.raises(HTTPException):
        validate_rating(0)  # Too low

    with pytest.raises(HTTPException):
        validate_rating(6)  # Too high


def test_detect_sql_injection():
    """Test SQL injection detection"""
    # Should detect SQL injection attempts
    assert detect_sql_injection("SELECT * FROM users") == True
    assert detect_sql_injection("'; DROP TABLE users--") == True
    assert detect_sql_injection("1 OR 1=1") == True

    # Normal queries should be fine
    assert detect_sql_injection("python programming") == False
    assert detect_sql_injection("web development") == False


def test_validate_search_query_valid():
    """Test valid search queries"""
    assert validate_search_query("python") == "python"
    assert validate_search_query("web development") == "web development"


def test_validate_search_query_invalid():
    """Test invalid search queries"""
    # Too short
    with pytest.raises(HTTPException):
        validate_search_query("p")

    # SQL injection attempt
    with pytest.raises(HTTPException):
        validate_search_query("'; DROP TABLE users--")
