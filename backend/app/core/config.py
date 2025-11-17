"""
Application configuration with Pydantic Settings
Comprehensive settings with validation and security best practices
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, EmailStr, AnyHttpUrl
from typing import List, Optional, Union
import secrets
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    All sensitive data should be in .env file
    """

    # ============= Environment =============
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Debug mode")

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    # ============= Project Info =============
    PROJECT_NAME: str = Field(default="CourseRate", description="Project name")
    VERSION: str = Field(default="1.0.0", description="API version")
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")
    API_V2_STR: str = Field(default="/api/v2", description="API v2 prefix (future)")

    # ============= Server =============
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Server port")
    WORKERS: int = Field(default=4, ge=1, le=16, description="Number of worker processes")
    RELOAD: bool = Field(default=False, description="Auto-reload on code changes")

    # ============= Database =============
    DATABASE_URL: str = Field(..., description="Database connection URL")
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=20, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1, le=60, description="Pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, ge=300, description="Pool recycle time in seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL queries (debug)")

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or v == "":
            raise ValueError("DATABASE_URL must be set")
        if v.startswith("sqlite") and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SQLite is not allowed in production")
        return v

    # ============= Security =============
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=5, le=1440, description="Access token lifetime")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, le=30, description="Refresh token lifetime")

    ENCRYPTION_KEY: Optional[str] = Field(default=None, description="Fernet encryption key for sensitive data")
    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=6, le=128)
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True)
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True)
    PASSWORD_REQUIRE_DIGITS: bool = Field(default=True)
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=False)

    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Allowed hosts")

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    # ============= CORS =============
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str], values) -> List[str]:
        # В production не разрешаем "*"
        if values.data.get("ENVIRONMENT") == "production" and "*" in v:
            raise ValueError("Wildcard CORS origin not allowed in production")
        return v

    # ============= Email (SMTP) =============
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP server host")
    SMTP_PORT: int = Field(default=587, ge=1, le=65535, description="SMTP server port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_FROM_EMAIL: Optional[EmailStr] = Field(default=None, description="From email address")
    SMTP_FROM_NAME: Optional[str] = Field(default="CourseRate", description="From name")
    SMTP_TLS: bool = Field(default=True, description="Use TLS")
    SMTP_SSL: bool = Field(default=False, description="Use SSL")
    ENABLE_EMAIL: bool = Field(default=False, description="Enable email sending")

    # ============= Redis =============
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    REDIS_DB: int = Field(default=0, ge=0, le=15, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_URL: Optional[str] = Field(default=None, description="Full Redis URL (overrides individual settings)")
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, ge=1, le=30)
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(default=5, ge=1, le=30)
    ENABLE_CACHE: bool = Field(default=False, description="Enable Redis caching")

    def get_redis_url(self) -> str:
        """Build Redis URL from components"""
        if self.REDIS_URL:
            return self.REDIS_URL
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ============= Logging =============
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    LOG_DIR: str = Field(default="logs", description="Directory for log files")
    LOG_FILE_MAX_BYTES: int = Field(default=10485760, description="Max log file size (10MB)")
    LOG_FILE_BACKUP_COUNT: int = Field(default=5, description="Number of log file backups")

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v_upper

    # ============= Rate Limiting =============
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_STORAGE: str = Field(default="memory://", description="Rate limit storage")
    RATE_LIMIT_DEFAULT: str = Field(default="200/minute", description="Default rate limit")
    RATE_LIMIT_LOGIN: str = Field(default="10/minute", description="Login rate limit")
    RATE_LIMIT_REGISTER: str = Field(default="5/hour", description="Registration rate limit")

    # ============= Anti-spam =============
    REVIEWS_PER_DAY_LIMIT: int = Field(default=5, ge=1, le=50, description="Max reviews per day per user")
    ACCOUNT_MIN_AGE_DAYS: int = Field(default=3, ge=0, le=30, description="Min account age to leave reviews")
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, ge=3, le=10, description="Max failed login attempts")
    LOGIN_ATTEMPT_TIMEOUT: int = Field(default=900, ge=60, description="Login attempt timeout in seconds")

    # ============= Pagination =============
    DEFAULT_PAGE_SIZE: int = Field(default=20, ge=1, le=100, description="Default pagination size")
    MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=1000, description="Maximum pagination size")

    # ============= File Upload =============
    MAX_UPLOAD_SIZE: int = Field(default=5242880, description="Max file upload size (5MB)")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "webp"],
        description="Allowed file extensions"
    )
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")

    # ============= Telegram Bot =============
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, description="Telegram bot token")
    TELEGRAM_ADMIN_IDS: List[int] = Field(default=[], description="Telegram admin chat IDs")
    ENABLE_TELEGRAM: bool = Field(default=False, description="Enable Telegram bot")

    # ============= Monitoring =============
    ENABLE_METRICS: bool = Field(default=False, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, ge=1, le=65535, description="Metrics server port")

    # ============= Sentry =============
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, ge=0.0, le=1.0, description="Sentry traces sample rate")
    ENABLE_SENTRY: bool = Field(default=False, description="Enable Sentry")

    # ============= Admin =============
    FIRST_SUPERUSER_EMAIL: Optional[EmailStr] = Field(default=None, description="First superuser email")
    FIRST_SUPERUSER_PASSWORD: Optional[str] = Field(default=None, description="First superuser password")
    ADMIN_EMAIL: Optional[EmailStr] = Field(default=None, description="Admin contact email")

    # ============= Features =============
    ENABLE_REGISTRATION: bool = Field(default=True, description="Allow new user registration")
    REQUIRE_EMAIL_VERIFICATION: bool = Field(default=False, description="Require email verification")
    ENABLE_SOCIAL_AUTH: bool = Field(default=False, description="Enable social authentication")
    ENABLE_TWO_FACTOR: bool = Field(default=False, description="Enable 2FA")

    # ============= Testing =============
    TESTING: bool = Field(default=False, description="Testing mode")
    TEST_DATABASE_URL: Optional[str] = Field(default=None, description="Test database URL")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"

    def is_staging(self) -> bool:
        """Check if running in staging"""
        return self.ENVIRONMENT == "staging"


# Global settings instance
settings = Settings()

# Validate critical settings on startup
if settings.is_production():
    assert settings.SECRET_KEY != secrets.token_urlsafe(32), "SECRET_KEY must be set in production"
    assert settings.DEBUG is False, "DEBUG must be False in production"
    assert "*" not in settings.BACKEND_CORS_ORIGINS, "Wildcard CORS not allowed in production"
